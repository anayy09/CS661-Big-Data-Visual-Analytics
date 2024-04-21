import vtk
from vtk.util.numpy_support import vtk_to_numpy

def rk4_integrate(probe_filter, point, step_size):
    def get_vector_at_point(point):
        # Set up a vtkPoints object and insert the current point
        vtk_point = vtk.vtkPoints()
        vtk_point.InsertNextPoint(point)

        # Create a vtkPolyData and set its points to the vtkPoints object
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_point)

        # Set the input for the probe filter
        probe_filter.SetInputData(polydata)

        # Update the probe filter to interpolate the vector at the point
        probe_filter.Update()

        # Get the interpolated vector
        probed_data = probe_filter.GetOutput()
        vectors = probed_data.GetPointData().GetVectors()
        if vectors is not None:
            return vtk_to_numpy(vectors)[0]
        else:
            return None

    # Compute the k terms
    k1 = get_vector_at_point(point)
    if k1 is None:
        return None

    k2 = get_vector_at_point(
        [p + 0.5 * step_size * k for p, k in zip(point, k1)])
    if k2 is None:
        return None

    k3 = get_vector_at_point(
        [p + 0.5 * step_size * k for p, k in zip(point, k2)])
    if k3 is None:
        return None

    k4 = get_vector_at_point([p + step_size * k for p, k in zip(point, k3)])
    if k4 is None:
        return None

    # Calculate the next position based on the k terms
    next_point = [p + step_size * (k1i + 2 * k2i + 2 * k3i + k4i) / 6.0
                  for p, k1i, k2i, k3i, k4i in zip(point, k1, k2, k3, k4)]

    return next_point


def within_bounds(point, bounds):
    return all(bounds[i] <= point[i//2] <= bounds[i+1] for i in range(0, len(bounds), 2))


def trace_streamline(seed_point, probe_filter, bounds, step_size=0.05, max_steps=1000):
    streamline_points = [seed_point]
    current_point = seed_point

    # Forward integration
    for _ in range(max_steps):
        next_point = rk4_integrate(probe_filter, current_point, step_size)
        if next_point is None or not within_bounds(next_point, bounds):
            break
        streamline_points.append(next_point)
        current_point = next_point

    current_point = seed_point
    # Backward integration
    for _ in range(max_steps):
        next_point = rk4_integrate(probe_filter, current_point, -step_size)
        if next_point is None or not within_bounds(next_point, bounds):
            break
        streamline_points.insert(0, next_point)
        current_point = next_point

    return streamline_points


# Prepare the VTK objects
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName("tornado3d_vector.vti")
reader.Update()
vector_field = reader.GetOutput()

probe_filter = vtk.vtkProbeFilter()
probe_filter.SetSourceData(vector_field)

# seed_point = (0, 0, 7)
seed_point = list(
    map(float, input("Enter the 3D seed location (x,y,z): ").split(',')))
bounds = vector_field.GetBounds()

# Perform the streamline tracing
streamline = trace_streamline(seed_point, probe_filter, bounds)

# Convert the streamline points to VTK objects and save
points_vtk = vtk.vtkPoints()
lines_vtk = vtk.vtkCellArray()

for i, point in enumerate(streamline):
    points_vtk.InsertNextPoint(point)
    if i > 0:
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, i - 1)
        line.GetPointIds().SetId(1, i)
        lines_vtk.InsertNextCell(line)

polydata = vtk.vtkPolyData()
polydata.SetPoints(points_vtk)
polydata.SetLines(lines_vtk)

writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName("streamline.vtp")
writer.SetInputData(polydata)
writer.Write()

print("Streamline written to 'streamline.vtp'")