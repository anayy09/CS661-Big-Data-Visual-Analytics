from vtkmodules.all import (
    vtkXMLImageDataReader, vtkColorTransferFunction, vtkPiecewiseFunction,
    vtkSmartVolumeMapper, vtkVolume, vtkVolumeProperty, vtkRenderer,
    vtkRenderWindow, vtkRenderWindowInteractor, vtkOutlineFilter, vtkPolyDataMapper, vtkActor
)

# Function to setup and return color transfer function
def create_color_transfer_function():
    color_tf = vtkColorTransferFunction()
    color_tf.AddRGBPoint(-4931.54, 0, 1, 1)
    color_tf.AddRGBPoint(-2508.95, 0, 0, 1)
    color_tf.AddRGBPoint(-1873.9, 0, 0, 0.5)
    color_tf.AddRGBPoint(-1027.16, 1, 0, 0)
    color_tf.AddRGBPoint(-298.031, 1, 0.4, 0)
    color_tf.AddRGBPoint(2594.97, 1, 1, 0)
    return color_tf

# Function to setup and return opacity transfer function
def create_opacity_transfer_function():
    opacity_tf = vtkPiecewiseFunction()
    opacity_tf.AddPoint(-4931.54, 1.0)
    opacity_tf.AddPoint(101.815, 0.002)
    opacity_tf.AddPoint(2594.97, 0.0)
    return opacity_tf

# Function to perform volume rendering
def volume_render(data, color_tf, opacity_tf, use_phong_shading):
    volume_mapper = vtkSmartVolumeMapper()
    volume_mapper.SetInputData(data)

    volume_property = vtkVolumeProperty()
    volume_property.SetColor(color_tf)
    volume_property.SetScalarOpacity(opacity_tf)
    volume_property.SetInterpolationTypeToLinear()

    if use_phong_shading:
        volume_property.ShadeOn()
        volume_property.SetAmbient(0.5)
        volume_property.SetDiffuse(0.5)
        volume_property.SetSpecular(0.5)
    else:
        volume_property.ShadeOff()

    volume = vtkVolume()
    volume.SetMapper(volume_mapper)
    volume.SetProperty(volume_property)

    outline_filter = vtkOutlineFilter()
    outline_filter.SetInputData(data)
    outline_mapper = vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline_filter.GetOutputPort())
    outline_actor = vtkActor()
    outline_actor.SetMapper(outline_mapper)
    outline_actor.GetProperty().SetColor(0, 0, 0)

    renderer = vtkRenderer()
    renderer.AddVolume(volume)
    renderer.AddActor(outline_actor)
    renderer.SetBackground(1, 1, 1)  # Set background to white for visibility

    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)
    render_window.SetWindowName('Volume Rendering')

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    reader = vtkXMLImageDataReader()
    reader.SetFileName("Data/Isabel_3D.vti")
    reader.Update()

    data = reader.GetOutput()
    color_tf = create_color_transfer_function()
    opacity_tf = create_opacity_transfer_function()

    phong_shading_input = input("Enable Phong shading? (y/n): ").strip().lower()
    use_phong_shading = phong_shading_input == 'y'

    volume_render(data, color_tf, opacity_tf, use_phong_shading)
