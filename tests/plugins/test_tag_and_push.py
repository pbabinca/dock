"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.
"""

from __future__ import print_function, unicode_literals

from dock.core import DockerTasker
from dock.inner import DockerBuildWorkflow
from dock.plugin import PostBuildPluginsRunner
from dock.plugins.post_tag_and_push import TagAndPushPlugin
from dock.util import ImageName
from tests.constants import LOCALHOST_REGISTRY, TEST_IMAGE, INPUT_IMAGE, MOCK

if MOCK:
    from tests.docker_mock import mock_docker


class Y(object):
    pass


class X(object):
    image_id = INPUT_IMAGE
    source = Y()
    source.dockerfile_path = None
    source.path = None
    base_image = ImageName(repo="qwe", tag="asd")


def test_tag_and_push_plugin(tmpdir):
    if MOCK:
        mock_docker()

    tasker = DockerTasker()
    workflow = DockerBuildWorkflow({"provider": "git", "uri": "asd"}, TEST_IMAGE)
    workflow.tag_conf.add_image(TEST_IMAGE)
    workflow.push_conf.add_docker_registry(LOCALHOST_REGISTRY, insecure=True)
    setattr(workflow, 'builder', X)

    runner = PostBuildPluginsRunner(
        tasker,
        workflow,
        [{
            'name': TagAndPushPlugin.key,
        }]
    )
    output = runner.run()
    image = output[TagAndPushPlugin.key][0]
    tasker.remove_image(image)
