from __future__ import print_function

from dock.core import DockerTasker
from dock.inner import DockerBuildWorkflow
from dock.plugin import PostBuildPluginsRunner
from dock.plugins.post_squash_layers import SquashLayersPlugin
from dock.plugins.post_tag_and_push import TagAndPushPlugin
from dock.plugins.post_tag_by_labels import TagByLabelsPlugin
from dock.util import ImageName
from tests.constants import LOCALHOST_REGISTRY, TEST_IMAGE, INPUT_IMAGE


class X(object):
    image_id = INPUT_IMAGE
    git_dockerfile_path = None
    git_path = None
    base_image = ImageName(repo="qwe", tag="asd")


def test_squash_layers_plugin(tmpdir):
    tasker = DockerTasker()
    workflow = DockerBuildWorkflow("asd", "test-image")

    setattr(workflow, 'builder', X)

    runner = PostBuildPluginsRunner(
        tasker,
        workflow,
        [{
            'name': SquashLayersPlugin.key,
            'args': {
                "image": INPUT_IMAGE,
            }
        }]
    )
    output = runner.run()
    assert output[SquashLayersPlugin.key]
