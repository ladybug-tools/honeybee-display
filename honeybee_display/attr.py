"""Display attribute objects for creating visualization sets."""


class RoomAttribute(object):
    """A Room attribute object.

    Args:
        name: A name for this Room Attribute.
        attr: A list of text strings of attributes that the Model Rooms have, which will
            be used to construct a visualization of this attribute in the resulting
            VisualizationSet. This can also be a list of attribute strings and a
            separate VisualizationData will be added to the AnalysisGeometry that
            represents the attribute in the resulting VisualizationSet (or a separate
            ContextGeometry layer if color is True). Attributes input here can have '.'
            that separates the nested attributes from one another. For example,
            'properties.energy.construction' or 'user_data.tag'

        color: A boolean to note whether the input room_attr should be expressed as a
            colored AnalysisGeometry. (Default: True)

        text: A boolean to note whether the input room_attr should be expressed as a
            a ContextGeometry as text labels. (Default: False)

        legend_par:An optional LegendParameter object to customize the display of the
            attribute. For text attribute only the text_height and font will be used to
            customize the text.
    """

    def __init__(
        self, name, attr, color=True, text=False, legend_par=None
            ):
        self.name = name
        self.attr = attr
        self.color = color
        self.text = text
        self.legend_par = legend_par


class FaceAttribute(RoomAttribute):
    """A Face attribute object.

    Args:
        name: A name for this Face Attribute.
        attr: A list of text strings of attributes the Model Faces have, which will
            be used to construct a visualization of this attribute in the resulting
            VisualizationSet. This can also be a list of attribute strings and a
            separate VisualizationData will be added to the AnalysisGeometry that
            represents the attribute in the resulting VisualizationSet (or a separate
            ContextGeometry layer if color is True). Attributes input here can have '.'
            that separates the nested attributes from one another. For example,
            'properties.energy.construction' or 'user_data.tag'

        color: A boolean to note whether the input room_attr should be expressed as a
            colored AnalysisGeometry. (Default: True)

        text: A boolean to note whether the input room_attr should be expressed as a
            a ContextGeometry as text labels. (Default: False)

        legend_par:An optional LegendParameter object to customize the display of the
            attribute. For text attribute only the text_height and font will be used to
            customize the text.

        face_types: List of face types to be included in the visualization set. By
            default all the faces will be exported to visualization set. Valid values
            are:

            * Wall
            * RoofCeiling
            * Floor
            * AirBoundary
            * Aperture
            * Shade

    """

    def __init__(self, name, attr, color=True, text=False, legend_par=None, face_types=None):
        super().__init__(name, attr, color, text, legend_par)
        self.face_types = face_types
