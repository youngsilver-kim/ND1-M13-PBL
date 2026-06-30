#!/usr/bin/env python3
"""test_sdf_utils.py — src/sdf_utils.py 단위 테스트
실행: cd ND1_M13_PBL && python3 -m pytest tests/ -v
"""
import sys, os, math, pytest
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))
from sdf_utils import SDFEditor, PhysicsCalc, GRAVITY, MU_CONDITIONS, DT_CONDITIONS

SAMPLE_SDF = """<?xml version="1.0"?>
<sdf version="1.8"><world name="test">
  <physics><max_step_size>0.001</max_step_size></physics>
  <model name="box"><link name="base"><collision name="col">
    <surface><friction><ode><mu>0.5</mu><mu2>0.5</mu2></ode></friction>
    <bounce><restitution_coefficient>0.2</restitution_coefficient></bounce></surface>
    <sensor name="imu"><imu><angular_velocity><z>
      <noise type="gaussian"><stddev>0.02</stddev></noise>
    </z></angular_velocity></imu></sensor>
  </collision></link></model>
</world></sdf>"""

@pytest.fixture
def tmp_sdf(tmp_path):
    f = tmp_path / "test.sdf"
    f.write_text(SAMPLE_SDF, encoding="utf-8")
    return str(f)

class TestPhysicsCalc:
    def test_friction_monotone(self):
        c = PhysicsCalc()
        assert c.friction_distance(0.1,v0=2.0,t=10) > c.friction_distance(1.0,v0=2.0,t=10)
    def test_friction_formula(self):
        c = PhysicsCalc(); mu,v0 = 0.5,2.0
        expected = v0**2/(2*mu*GRAVITY)
        assert abs(c.friction_distance(mu,v0=v0,t=100)-expected)<0.001
    def test_pendulum_period(self):
        T = PhysicsCalc().pendulum_period(1.0)
        assert abs(T - 2*math.pi*math.sqrt(1/GRAVITY))<1e-6
    def test_euler_error_monotone(self):
        c = PhysicsCalc()
        assert c.euler_energy_error(0.01) > c.euler_energy_error(0.001)
    def test_euler_stable_dt(self):
        assert PhysicsCalc().euler_energy_error(dt=0.001, t_max=5) < 5.0

class TestSDFEditor:
    def test_set_friction(self,tmp_sdf):
        ed=SDFEditor(tmp_sdf); ed.set_friction(0.1)
        assert abs(ed.get_params().get("mu",-1)-0.1)<1e-6
    def test_set_timestep(self,tmp_sdf):
        ed=SDFEditor(tmp_sdf); ed.set_timestep(0.005)
        assert abs(ed.get_params().get("dt",-1)-0.005)<1e-8
    def test_set_imu_noise(self,tmp_sdf):
        ed=SDFEditor(tmp_sdf); ed.set_imu_noise(0.1)
        assert abs(ed.get_params().get("stddev",-1)-0.1)<1e-6
    def test_chaining(self,tmp_sdf):
        ed=SDFEditor(tmp_sdf); ed.set_friction(0.3).set_timestep(0.002)
        p=ed.get_params(); assert abs(p["mu"]-0.3)<1e-6 and abs(p["dt"]-0.002)<1e-8
    def test_restore(self,tmp_sdf):
        ed=SDFEditor(tmp_sdf); ed.set_friction(0.9); ed.restore()
        assert abs(ed.get_params().get("mu",-1)-0.5)<1e-6
    def test_invalid_mu(self,tmp_sdf):
        with pytest.raises(ValueError): SDFEditor(tmp_sdf).set_friction(-1.0)
    def test_invalid_dt(self,tmp_sdf):
        with pytest.raises(ValueError): SDFEditor(tmp_sdf).set_timestep(0.0)
    def test_invalid_sigma(self,tmp_sdf):
        with pytest.raises(ValueError): SDFEditor(tmp_sdf).set_imu_noise(-0.01)
    def test_save_persists(self,tmp_sdf):
        ed=SDFEditor(tmp_sdf); ed.set_friction(0.8); ed.save()
        assert abs(SDFEditor(tmp_sdf).get_params().get("mu",-1)-0.8)<1e-6
