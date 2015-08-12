# Copyright 2015 Huawei Technologies Co., Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib

from django.core.urlresolvers import reverse
import mock

from mistraldashboard.test import helpers as test

INDEX_URL = reverse('horizon:mistral:workflows:index')
CREATE_URL = reverse('horizon:mistral:workflows:create')


class WorkflowsTest(test.TestCase):

    def test_index(self):
        with contextlib.nested(
            mock.patch('mistraldashboard.api.workflow_list',
                       return_value=self.mistralclient_workflows.list()),):
            res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'mistral/workflows/index.html')

    def test_create_get(self):
        res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(res, 'mistral/workflows/create.html')

    def test_create_post(self):
        workflow = self.mistralclient_workflows.first()

        url = reverse('horizon:mistral:workflows:select_definition')
        res = self.client.get(url)
        self.assertTemplateUsed(
            res,
            'mistral/workflows/select_definition.html'
        )
        form_data = {
            'definition_source': 'raw',
            'definition_data': workflow.definition
        }
        with contextlib.nested(
            mock.patch('mistraldashboard.api.workflow_validate',
                       return_value={'valid': True}),) as (mocked_validate,):
            res = self.client.post(url, form_data)

        self.assertTemplateUsed(res, 'mistral/workflows/create.html')
        mocked_validate.assert_called_once_with(
            mock.ANY,
            workflow.definition
        )

        form_data = {
            'definition': workflow.definition
        }
        with contextlib.nested(
            mock.patch('mistraldashboard.api.workflow_create',
                       return_value=workflow),) as (mocked_create,):
            res = self.client.post(CREATE_URL, form_data)
        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        mocked_create.assert_called_once_with(
            mock.ANY,
            workflow.definition
        )