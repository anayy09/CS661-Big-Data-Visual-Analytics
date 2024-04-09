# Importing necessary VTK modules for data processing and visualization
from vtk import *

# Function to load the dataset and extract the isocontour
def extract_isocontour(file_path, output_path, isovalue):
    # Load the dataset
    reader = vtkXMLImageDataReader()
    reader.SetFileName(file_path)
    reader.Update()
    data = reader.GetOutput()

    # Initialize points and cell array for contour lines
    points = vtkPoints()
    cells = vtkCellArray()

    # Retrieve pressure data
    pressure_data = data.GetPointData().GetArray('Pressure')

    # Isocontour extraction logic
    for cell_id in range(data.GetNumberOfCells()):
        cell = data.GetCell(cell_id)
        point_ids = [cell.GetPointId(i) for i in range(4)]
        coords = [data.GetPoint(pid) for pid in point_ids]
        values = [pressure_data.GetTuple1(pid) for pid in point_ids]

        # Check each edge for intersections with the isovalue
        for i in range(4):
            next_i = (i + 1) % 4
            if (values[i] - isovalue) * (values[next_i] - isovalue) < 0:
                # Linear interpolation to find intersection point
                t = (isovalue - values[i]) / (values[next_i] - values[i])
                intersection = [coords[i][j] + t * (coords[next_i][j] - coords[i][j]) for j in range(3)]
                pid = points.InsertNextPoint(intersection)
                if i % 2 == 0:  # Connect points to form a line
                    line = vtkPolyLine()
                    line.GetPointIds().SetNumberOfIds(2)
                    line.GetPointIds().SetId(0, pid - 1)
                    line.GetPointIds().SetId(1, pid)
                    cells.InsertNextCell(line)

    # Create and write the polydata containing the isocontour
    poly_data = vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.SetLines(cells)
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(output_path)
    writer.SetInputData(poly_data)
    writer.Write()

# Main function to run the extraction
if __name__ == "__main__":
    file_path = 'Data/Isabel_2D.vti'
    output_path = 'task1.vtp'
    isovalue = float(input("Please enter the isovalue within the range (-1438, 630): "))
    extract_isocontour(file_path, output_path, isovalue)
    print(f"Isocontour extraction completed. Output saved to {output_path}.")
