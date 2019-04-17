# Copyright (c) XXXX, XXXX.
# See LICENSE file for details.

# This software is distributed WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

"""
Solve

du/dt + u * grad(u - w) = grad(p) + nu * div(grad(u))

Explain the numerics
"""

from turtleFSI.modules.common import *
from dolfin import Constant, inner, inv, grad, div


def fluid_setup(v_, p_, d_, n, psi, gamma, dx_f, ds, mu_f, rho_f, k, dt, v_deg, theta,
                **namespace):
    theta0 = Constant(theta)
    theta1 = Constant(1 - theta)

    # Temporal derivative
    F_fluid_nonlinear = rho_f/k * inner(J_(d_["n"]) * theta0 * (v_["n"] - v_["n-1"]), psi) * dx_f
    F_fluid_linear = rho_f/k * inner(J_(d_["n-1"]) * theta1 * (v_["n"] - v_["n-1"]), psi) * dx_f

    # Convection
    F_fluid_nonlinear = theta0 * rho_f * inner(J_(d_["n"]) * grad(v_["n"]) *
                                               inv(F_(d_["n"])) * v_["n"], psi) * dx_f
    F_fluid_linear += theta1 * rho_f * inner(J_(d_["n-1"]) * grad(v_["n-1"]) *
                                             inv(F_(d_["n-1"])) * v_["n-1"], psi) * dx_f

    # Stress from pressure
    F_fluid_nonlinear += inner(J_(d_["n"]) * sigma_f_p(p_["n"], d_["n"]) *
                               inv(F_(d_["n"])).T, grad(psi)) * dx_f

    # Stress for velocity
    F_fluid_nonlinear += theta0 * inner(J_(d_["n"]) * sigma_f_u(v_["n"], d_["n"], mu_f) *
                                        inv(F_(d_["n"])).T, grad(psi)) * dx_f
    F_fluid_linear += theta1 * inner(J_(d_["n-1"]) * sigma_f_u(v_["n-1"], d_["n-1"], mu_f)
                                     * inv(F_(d_["n-1"])).T, grad(psi)) * dx_f

    # Divergence free term
    F_fluid_nonlinear += inner(div(J_(d_["n"]) * inv(F_(d_["n"])) * v_["n"]), gamma) * dx_f

    # ALE term
    F_fluid_nonlinear -= rho_f * inner(J_(d_["n"]) * grad(v_["n"]) * inv(F_(d_["n"])) *
                                       ((d_["n"] - d_["n-1"])/k), psi) * dx_f

    return dict(F_fluid_linear=F_fluid_linear, F_fluid_nonlinear=F_fluid_nonlinear)