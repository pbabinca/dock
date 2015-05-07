from dock.plugin import PostBuildPlugin


__all__ = ('SquashLayersPlugin', )


class SquashLayersPlugin(PostBuildPlugin):
    key = "squash_layers"
    can_fail = False

    def __init__(self, tasker, workflow, image):
        """
        constructor

        :param tasker: DockerTasker instance
        :param workflow: DockerBuildWorkflow instance
        :param image: str, image to squash
        """
        # call parent constructor
        super(SquashLayersPlugin, self).__init__(tasker, workflow)
        self.image = image

    def run(self):
        container = self.tasker.d.create_container(self.image, "true")
        # inspect_json = self.tasker.inspect_image(self.image)

        response = self.tasker.d.export(container)
        self.log.debug("response = '%s'", response)

        it = response.read_chunked()
        self.log.debug("it = '%s'", it)

        import_response = self.tasker.d.import_image_from_stream(it, "test-squqash-im", "latest")
        self.log.debug("import_response = '%s'", import_response)

        # FIXME: add metadata, there are none at this point

        self.tasker.remove_container(container)

        return import_response
