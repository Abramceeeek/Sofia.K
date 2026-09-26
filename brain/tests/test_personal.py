import numpy as np

from brain.personal import Observation, fit_delta, log_posterior, loglik_terms, prior_only, prob_negative


def test_ordered_logit_derivatives_match_finite_differences():
    cut = (-2.0, -0.75, 0.75, 2.0)
    for y in range(5):
        for eta in (-3.0, -0.4, 0.0, 1.1, 2.7):
            o = Observation(x=np.zeros(1), y=y, cutpoints=cut)
            ll, d1, d2 = loglik_terms(eta, o)
            h = 1e-5
            lp, _, _ = loglik_terms(eta + h, o)
            lm, _, _ = loglik_terms(eta - h, o)
            assert abs((lp - lm) / (2 * h) - d1) < 1e-5
            _, d1p, _ = loglik_terms(eta + h, o)
            _, d1m, _ = loglik_terms(eta - h, o)
            assert abs((d1p - d1m) / (2 * h) - d2) < 1e-4
            assert d2 < 0  # log-concave


def test_ordered_probabilities_sum_to_one():
    cut = (-1.0, 1.0)
    for eta in (-2.0, 0.3, 4.0):
        total = sum(np.exp(loglik_terms(eta, Observation(np.zeros(1), y, cutpoints=cut))[0]) for y in range(3))
        assert abs(total - 1.0) < 1e-12


def test_no_data_returns_the_prior():
    sd = np.array([0.5, 1.0])
    post = fit_delta(np.zeros(3), np.array([0, 2]), sd, [])
    assert np.allclose(post.mean, 0)
    assert np.allclose(post.sd(), sd)
    assert np.allclose(prior_only(sd).precision, post.precision)


def test_recovers_the_sign_of_a_personal_weight_and_shrinks_uncertainty():
    rng = np.random.default_rng(7)
    b_pop = np.array([0.0, -0.3, 0.2])
    personal = np.array([0, 1])
    sd = np.array([0.75, 0.75])
    true_delta = np.array([1.2, -0.8])
    b_true = b_pop.copy()
    b_true[personal] += true_delta
    cut = (-2.0, -0.75, 0.75, 2.0)
    obs = []
    for _ in range(150):
        x = rng.uniform(0, 1, 3)
        eta = x @ b_true
        # sample an ordered-logit outcome
        u = rng.uniform()
        cdf = [1 / (1 + np.exp(-(c - eta))) for c in cut] + [1.0]
        y = next(k for k, c in enumerate(cdf) if u <= c)
        obs.append(Observation(x=x, y=y, cutpoints=cut))
    post = fit_delta(b_pop, personal, sd, obs)
    assert np.sign(post.mean[0]) == 1 and np.sign(post.mean[1]) == -1
    assert np.all(post.sd() < sd)
    # the MAP is a maximum of the log posterior
    lp = log_posterior(post.mean, b_pop, personal, sd, obs)
    for step in (np.array([0.05, 0]), np.array([0, -0.05])):
        assert log_posterior(post.mean + step, b_pop, personal, sd, obs) <= lp


def test_binary_choices_move_the_weight_toward_the_chosen_side():
    # Person always picks the plan with the shorter transfer: the transfer weight should fall.
    b_pop = np.array([-0.3])
    obs = [Observation(x=np.array([-1.0]), y=1) for _ in range(10)]  # x_A − x_B: A has less transfer
    post = fit_delta(b_pop, np.array([0]), np.array([0.75]), obs)
    assert post.mean[0] < 0


def test_prob_negative():
    assert abs(prob_negative(0.0, 1.0) - 0.5) < 1e-12
    assert prob_negative(-2.0, 1.0) > 0.97
    assert prob_negative(2.0, 1.0) < 0.03
