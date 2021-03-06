"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.
"""

from dock.plugin import PostBuildPlugin


__all__ = ('TagByLabelsPlugin', )


class TagByLabelsPlugin(PostBuildPlugin):
    """
    Use labels Name, Version and Release of final image and create tags:
     * Name:Version
     * Name:Version_Release
    """
    key = "tag_by_labels"
    can_fail = False

    def __init__(self, tasker, workflow, **kwargs):
        """
        constructor

        :param tasker: DockerTasker instance
        :param workflow: DockerBuildWorkflow instance
        """
        # call parent constructor
        super(TagByLabelsPlugin, self).__init__(tasker, workflow)
        self.log.warning("Ignoring arguments %s", kwargs)

    def run(self):
        if not self.workflow.built_image_inspect:
            raise RuntimeError("There are no inspect data of built image. "
                               "Have the build succeeded?")
        if "Labels" not in self.workflow.built_image_inspect["ContainerConfig"]:
            raise RuntimeError("No labels specified.")

        def get_label(label_name):
            try:
                return self.workflow.built_image_inspect["ContainerConfig"]["Labels"][label_name]
            except KeyError:
                raise RuntimeError("Missing label '%s'.", label_name)

        name = get_label("Name")
        version = get_label("Version")
        release = get_label("Release")

        nvr = "%s:%s_%s" % (name, version, release)
        nv = "%s:%s" % (name, version)

        self.workflow.tag_conf.add_images([nvr, nv])
