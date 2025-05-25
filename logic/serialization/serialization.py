import json
import numpy as np
from typing import Any
import uuid

from models import BandStructure, BasisVector, Site, State, UnitCell


class UnitCellEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for UnitCell objects and their components.

    Handles serialization of custom types to JSON-compatible formats:
    - UUID objects are converted to strings
    - NumPy complex values are converted to [real, imag] lists
    - NumPy arrays are converted to lists
    - BasisVector, State, Site, and UnitCell objects are converted to dicts
    - Dictionaries with UUID keys are converted to dicts with string keys
    - Tuples with UUID elements are converted to strings
    """

    def default(self, obj):
        # Handle UUID objects
        if isinstance(obj, uuid.UUID):
            return str(obj)

        # Handle NumPy complex numbers
        if isinstance(obj, complex) or np.issubdtype(
            type(obj), np.complexfloating
        ):
            return [obj.real, obj.imag]

        # Handle NumPy arrays
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # Handle BandStructure objects
        if isinstance(obj, BandStructure):
            return {
                "type": "BandStructure",
                "path": [x.tolist() for x in obj.path],
                "special_points": [x.tolist() for x in obj.special_points],
                "eigenvalues": [x.tolist() for x in obj.eigenvalues],
                "eigenvectors": [x.tolist() for x in obj.eigenvectors],
            }

        # Handle BasisVector objects
        if isinstance(obj, BasisVector):
            return {
                "type": "BasisVector",
                "x": obj.x,
                "y": obj.y,
                "z": obj.z,
                "is_periodic": obj.is_periodic,
            }

        # Handle State objects
        if isinstance(obj, State):
            return {"type": "State", "name": obj.name, "id": obj.id}

        # Handle Site objects
        if isinstance(obj, Site):
            # Convert states dictionary to have string keys
            states_dict = {str(k): v for k, v in obj.states.items()}
            return {
                "type": "Site",
                "name": obj.name,
                "c1": obj.c1,
                "c2": obj.c2,
                "c3": obj.c3,
                "R": obj.R,
                "color": obj.color,
                "states": states_dict,
                "id": obj.id,
            }

        # Handle UnitCell objects
        if isinstance(obj, UnitCell):
            # Convert sites dictionary to have string keys
            sites_dict = {str(k): v for k, v in obj.sites.items()}

            # Convert hoppings dictionary with tuple keys to string keys
            hoppings_dict = {
                f"{str(k[0])},{str(k[1])}": v for k, v in obj.hoppings.items()
            }

            return {
                "type": "UnitCell",
                "name": obj.name,
                "v1": obj.v1,
                "v2": obj.v2,
                "v3": obj.v3,
                "sites": sites_dict,
                "hoppings": hoppings_dict,
                "bandstructure": obj.bandstructure,
                "id": obj.id,
            }

        # Let the parent class handle all other types
        return super().default(obj)


def decode_unit_cell_json(json_obj: dict[str, Any]) -> Any:
    """
    Decode JSON objects into their appropriate custom types.

    This is used as the object_hook for json.loads() to deserialize
    JSON data back into UnitCell, Site, State, and BasisVector objects.

    Args:
        json_obj: A dictionary representing a JSON object

    Returns:
        The appropriate Python object based on the 'type' field
    """
    # Check if this is one of our custom types
    if "type" in json_obj:
        obj_type = json_obj["type"]

        # Handle BandStructure
        if obj_type == "BandStructure":
            return BandStructure(
                path=[np.array(x) for x in json_obj["path"]],
                special_points=[
                    np.array(x) for x in json_obj["special_points"]
                ],
                eigenvalues=[np.array(x) for x in json_obj["eigenvalues"]],
                eigenvectors=[
                    np.array(
                        [
                            [
                                complex(real=real, imag=imag)
                                for real, imag in row
                                # Destructure each length-2 list
                            ]
                            for row in mat
                        ],
                        dtype=np.complex128,
                    )
                    for mat in json_obj[
                        "eigenvectors"
                    ]  # Each mat corresponds to a momentum point
                ],
            )

        # Handle BasisVector
        elif obj_type == "BasisVector":
            return BasisVector(
                x=json_obj["x"],
                y=json_obj["y"],
                z=json_obj["z"],
                is_periodic=json_obj["is_periodic"],
            )

        # Handle State
        elif obj_type == "State":
            return State(name=json_obj["name"], id=uuid.UUID(json_obj["id"]))

        # Handle Site
        elif obj_type == "Site":
            site = Site(
                name=json_obj["name"],
                c1=json_obj["c1"],
                c2=json_obj["c2"],
                c3=json_obj["c3"],
                R=json_obj["R"],
                color=tuple(json_obj["color"]),
                id=uuid.UUID(json_obj["id"]),
            )
            # Convert state dict with string keys back to UUID keys
            for state_id_str, state in json_obj["states"].items():
                site.states[uuid.UUID(state_id_str)] = state
            return site

        # Handle UnitCell
        elif obj_type == "UnitCell":
            unit_cell = UnitCell(
                name=json_obj["name"],
                v1=json_obj["v1"],
                v2=json_obj["v2"],
                v3=json_obj["v3"],
                bandstructure=json_obj["bandstructure"],
                id=uuid.UUID(json_obj["id"]),
            )

            # Convert sites dict with string keys back to UUID keys
            for site_id_str, site in json_obj["sites"].items():
                unit_cell.sites[uuid.UUID(site_id_str)] = site

            # Convert hoppings dict with tuple of string keys back to tuple of
            # UUID keys and convert complex values from [real, imag] format
            # back to complex numbers
            for hopping_key_str, hopping_values in json_obj[
                "hoppings"
            ].items():
                # Parse the string key '(uuid1, uuid2)' back to tuple of UUIDs
                k1_str, k2_str = hopping_key_str.split(",")
                key = (uuid.UUID(k1_str), uuid.UUID(k2_str))

                # Convert the hopping values: [(displacement, amplitude), ...]
                converted_values = []
                for displacement_list, amplitude_list in hopping_values:
                    # displacement = (
                    #     displacement_list[0],
                    #     displacement_list[1],
                    #     displacement_list[2],
                    # )
                    displacement = tuple(displacement_list)
                    # Convert [real, imag] list back to complex
                    amplitude = complex(amplitude_list[0], amplitude_list[1])
                    converted_values.append((displacement, amplitude))

                unit_cell.hoppings[key] = converted_values

            return unit_cell

    # If not a custom type, return the object as is
    return json_obj


def serialize_unit_cells(unit_cells: dict[uuid.UUID, UnitCell]) -> str:
    """
    Serialize a dictionary of UnitCell objects to a JSON string.

    Parameters
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects

    Returns
    -------
    str
        JSON string representation of the unit_cells dictionary
    """
    # Convert dictionary with UUID keys to string keys for JSON serialization
    serializable_dict = {str(k): v for k, v in unit_cells.items()}
    return json.dumps(serializable_dict, cls=UnitCellEncoder, indent=2)


def deserialize_unit_cells(json_str: str) -> dict[uuid.UUID, UnitCell]:
    """
    Deserialize a JSON string back into a dictionary of UnitCell objects.

    Parameters
    json_str : str
        JSON string representation of unit_cells dictionary

    Returns
    -------
    dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    """
    # Parse the JSON string with custom object hook
    string_keyed_dict = json.loads(json_str, object_hook=decode_unit_cell_json)

    # Convert string keys back to UUID keys
    return {uuid.UUID(k): v for k, v in string_keyed_dict.items()}
