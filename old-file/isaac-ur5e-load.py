from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.sensor import Camera
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.types import ArticulationAction
from omni.isaac.core.utils.viewports import set_camera_view
from omni.isaac.core.objects import VisualSphere, GroundPlane
import numpy as np
import pathlib
import omni.ui as ui
import functools


usd_path = pathlib.Path(__file__).parent / "/qyy-assets/qyy-hande-table.usd"

create_prim(
    prim_path="/World/ur5_hande",
    usd_path=str(usd_path),
    prim_type="Xform"
)
robot_articulation = Articulation(prim_path="/World/ur5_hande")


the_world = World(stage_units_in_meters=1.0)    
the_world.scene.add(robot_articulation) # type: ignore

# site_gel_0=VisualSphere(
#     prim_path="/World/ur5_hande/gelsight_0/site",
#     color=np.array([1.0 ,0.0 ,0.0]),
#     scale=[0.01],
#     translation=np.array([0.0175, 0.0173, 0.016]),# type:ignore
#     visible=True
#     )
# site_gel_1=VisualSphere(
#     prim_path="/World/ur5_hande/gelsight_1/site",
#     color=np.array([1.0 ,0.0 ,0.0]),
#     scale=[0.01],
#     translation=np.array([0.0175, 0.0173, 0.016]), # type:ignore
#     visible=True
#     )
# site_object = VisualSphere(
#     prim_path='/World/table/object/site',
#     color=np.array([0.0, 1.0, 0.0]),
#     scale=[0.01],
#     translation=np.array([0.01, -0.01, -0.005]),
#     visible=True
# )

the_world.reset()
robot_articulation.initialize()

robot_articulation.enable_gravity()
controller = robot_articulation.get_articulation_controller()
joint_names = robot_articulation.dof_names

# --- Use dof_properties to get joint limits ---
dof_properties = robot_articulation.dof_properties
lower_limits = [prop["lower"] for prop in dof_properties]
upper_limits = [prop["upper"] for prop in dof_properties]

# Convert to degrees for the UI
lower_deg = np.degrees(lower_limits)
upper_deg = np.degrees(upper_limits)

# Store joint values using UI models
joint_models = [ui.SimpleFloatModel() for _ in joint_names]

window = ui.Window("Joint Control", width=400, height=300)
with window.frame:
    with ui.VStack():
        for i, joint in enumerate(joint_names):
            ui.FloatSlider(
                min=lower_deg[i], max=upper_deg[i], step=1.0,
                model=joint_models[i],
                name=joint
            )

while simulation_app.is_running():
    joint_values_deg = [model.get_value_as_float() for model in joint_models]
    print(joint_values_deg)
    joint_values_rad = np.radians(joint_values_deg)
    action = ArticulationAction(joint_values_rad)
    controller.apply_action(action)
    the_world.step(render=True)

simulation_app.close()


