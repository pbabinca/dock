"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.
"""

from __future__ import unicode_literals

import json
import os
from dock.core import DockerTasker
from dock.inner import DockerBuildWorkflow
from dock.plugin import PreBuildPluginsRunner, PostBuildPluginsRunner, InputPluginsRunner
from dock.plugins.post_rpmqa import PostBuildRPMqaPlugin
from dock.util import ImageName
from tests.constants import DOCKERFILE_GIT


TEST_IMAGE = "fedora:latest"
SOURCE = {"provider": "git", "uri": DOCKERFILE_GIT}


def test_load_prebuild_plugins():
    runner = PreBuildPluginsRunner(DockerTasker(), DockerBuildWorkflow(SOURCE, ""), None)
    assert runner.plugin_classes is not None
    assert len(runner.plugin_classes) > 0


def test_load_postbuild_plugins():
    runner = PostBuildPluginsRunner(DockerTasker(), DockerBuildWorkflow(SOURCE, ""), None)
    assert runner.plugin_classes is not None
    assert len(runner.plugin_classes) > 0


class X(object):
    pass


def test_rpmqa_plugin():
    tasker = DockerTasker()
    workflow = DockerBuildWorkflow(SOURCE, "test-image")
    setattr(workflow, 'builder', X())
    setattr(workflow.builder, 'image_id', "asd123")
    setattr(workflow.builder, 'base_image', ImageName(repo='fedora', tag='21'))
    setattr(workflow.builder, "source", X())
    setattr(workflow.builder.source, 'dockerfile_path', "/non/existent")
    setattr(workflow.builder.source, 'path', "/non/existent")
    runner = PostBuildPluginsRunner(tasker, workflow,
                                    [{"name": PostBuildRPMqaPlugin.key,
                                      "args": {'image_id': TEST_IMAGE}}])
    results = runner.run()
    assert results is not None
    assert results[PostBuildRPMqaPlugin.key] is not None
    assert len(results[PostBuildRPMqaPlugin.key]) > 0


def test_substitution(tmpdir):
    tmpdir_path = str(tmpdir)
    build_json_path = os.path.join(tmpdir_path, "build.json")
    with open(build_json_path, 'w') as fp:
        json.dump({
            "image": "some-image"
        }, fp)
    changed_image_name = "changed-image-name"
    runner = InputPluginsRunner([{"name": "path",
                                  "args": {
                                      "path": build_json_path,
                                      "substitutions": {
                                          "image": changed_image_name
    }}}])
    results = runner.run()
    assert results['path']['image'] == changed_image_name


def test_substitution_on_plugins(tmpdir):
    tmpdir_path = str(tmpdir)
    build_json_path = os.path.join(tmpdir_path, "build.json")
    with open(build_json_path, 'w') as fp:
        json.dump({
            "image": "some-image",
            "prebuild_plugins": [{
                'name': 'asd',
                'args': {
                    'key': 'value1'
                }
            }]
        }, fp)
    changed_value = "value-123"
    runner = InputPluginsRunner([{"name": "path",
                                  "args": {"path": build_json_path,
                                           "substitutions": {
                                               "prebuild_plugins.asd.key": changed_value}}}])
    results = runner.run()
    assert results['path']['prebuild_plugins'][0]['args']['key'] == changed_value
