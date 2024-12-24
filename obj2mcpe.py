import json
import os
import sys
from pathlib import Path
import struct

def obj_to_bedrock_entity(obj_path, texture_width=64, texture_height=64):
    obj_name = Path(obj_path).stem
    bedrock_model = {
        f"geometry.{obj_name}": {
            "texturewidth": texture_width,
            "textureheight": texture_height,
            "bones": []
        }
    }

    bone = {
        "name": "head",
        "pivot": [0, 0, 0],
        "rotation": [0, 0, 0],
        "cubes": []
    }

    with open(obj_path, "r") as obj_file:
        vertices = []
        for line in obj_file:
            if line.startswith("v "):  # Vertex line
                _, x, y, z = line.split()
                vertices.append((float(x), float(y), float(z)))
            elif line.startswith("f "):  # Face line
                face_indices = [int(index.split("/")[0]) - 1 for index in line.split()[1:]]
                face_vertices = [vertices[i] for i in face_indices]

                x_coords, y_coords, z_coords = zip(*face_vertices)
                cube = {
                    "origin": [
                        min(x_coords),
                        min(y_coords),
                        min(z_coords)
                    ],
                    "size": [
                        max(x_coords) - min(x_coords),
                        max(y_coords) - min(y_coords),
                        max(z_coords) - min(z_coords)
                    ],
                    "uv": [0, 0]
                }
                bone["cubes"].append(cube)

    bedrock_model[f"geometry.{obj_name}"]["bones"].append(bone)

    output_path = f"{obj_name}.geo.json"
    with open(output_path, "w") as json_file:
        json.dump(bedrock_model, json_file, indent=4)

    print(f"Bedrock model saved to {output_path}")

def stl_to_bedrock_entity(stl_path, texture_width=64, texture_height=64):
    stl_name = Path(stl_path).stem
    bedrock_model = {
        f"geometry.{stl_name}": {
            "texturewidth": texture_width,
            "textureheight": texture_height,
            "bones": []
        }
    }

    bone = {
        "name": "head",
        "pivot": [0, 0, 0],
        "rotation": [0, 0, 0],
        "cubes": []
    }

    with open(stl_path, "rb") as stl_file:
        header = stl_file.read(80)
        num_triangles = struct.unpack('<I', stl_file.read(4))[0]

        for _ in range(num_triangles):
            stl_file.read(12)  # Normal vector, not used
            vertices = []
            for _ in range(3):
                vertices.append(struct.unpack('<fff', stl_file.read(12)))
            x_coords, y_coords, z_coords = zip(*vertices)
            cube = {
                "origin": [
                    min(x_coords),
                    min(y_coords),
                    min(z_coords)
                ],
                "size": [
                    max(x_coords) - min(x_coords),
                    max(y_coords) - min(y_coords),
                    max(z_coords) - min(z_coords)
                ],
                "uv": [0, 0]
            }
            bone["cubes"].append(cube)
            stl_file.read(2)  # Attribute byte count

    bedrock_model[f"geometry.{stl_name}"]["bones"].append(bone)

    output_path = f"{stl_name}.geo.json"
    with open(output_path, "w") as json_file:
        json.dump(bedrock_model, json_file, indent=4)

    print(f"Bedrock model saved to {output_path}")

def ply_to_bedrock_entity(ply_path, texture_width=64, texture_height=64):
    ply_name = Path(ply_path).stem
    bedrock_model = {
        f"geometry.{ply_name}": {
            "texturewidth": texture_width,
            "textureheight": texture_height,
            "bones": []
        }
    }

    bone = {
        "name": "head",
        "pivot": [0, 0, 0],
        "rotation": [0, 0, 0],
        "cubes": []
    }

    with open(ply_path, "r") as ply_file:
        vertices = []
        faces = []
        header = True
        vertex_count = 0
        face_count = 0
        line_index = 0

        for line in ply_file:
            line = line.strip()

            if header:
                if line.startswith("element vertex"):
                    vertex_count = int(line.split()[-1])
                elif line.startswith("element face"):
                    face_count = int(line.split()[-1])
                elif line.startswith("end_header"):
                    header = False
                continue

            # Process vertex data
            if line_index < vertex_count:
                parts = line.split()
                x, y, z = map(float, parts[:3])  # Use only the first three values
                vertices.append((x, y, z))
                line_index += 1
            # Process face data
            elif line_index < vertex_count + face_count:
                face_indices = list(map(int, line.split()[1:]))
                face_vertices = [vertices[i] for i in face_indices]

                if len(face_vertices) >= 3:  # Ensure at least a triangle
                    x_coords, y_coords, z_coords = zip(*face_vertices)
                    cube = {
                        "origin": [
                            min(x_coords),
                            min(y_coords),
                            min(z_coords)
                        ],
                        "size": [
                            max(x_coords) - min(x_coords),
                            max(y_coords) - min(y_coords),
                            max(z_coords) - min(z_coords)
                        ],
                        "uv": [0, 0]
                    }
                    bone["cubes"].append(cube)
                line_index += 1

    bedrock_model[f"geometry.{ply_name}"]["bones"].append(bone)

    output_path = f"{ply_name}.geo.json"
    with open(output_path, "w") as json_file:
        json.dump(bedrock_model, json_file, indent=4)

    print(f"Bedrock model saved to {output_path}")


if __name__ == "__main__":
    try:
        model_path = str(sys.argv[1]).replace("\\", "/")
        file_extension = Path(model_path).suffix.lower()

        if file_extension == ".obj":
            obj_to_bedrock_entity(model_path)
        elif file_extension == ".stl":
            stl_to_bedrock_entity(model_path)
        elif file_extension == ".ply":
            ply_to_bedrock_entity(model_path)
        else:
            print("Unsupported file format. Supported formats are: OBJ, STL, PLY.")
            sys.exit(1)
    except IndexError:
        print(f"Requires a model file as an argument:\n    python {os.path.basename(__file__)} [ModelFilePath]")
        sys.exit(1)
