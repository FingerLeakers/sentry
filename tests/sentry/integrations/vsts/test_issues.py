from __future__ import absolute_import

import responses

from exam import fixture
from django.test import RequestFactory
from time import time

from sentry.integrations.vsts.integration import VstsIntegration
from sentry.models import Identity, IdentityProvider, Integration
from sentry.testutils import TestCase
from sentry.utils import json

from .testutils import WORK_ITEM_RESPONSE


class VstsIssueSycnTest(TestCase):
    @fixture
    def request(self):
        return RequestFactory()

    def setUp(self):
        self.user = self.create_user()
        self.organization = self.create_organization(owner=self.user)

        model = Integration.objects.create(
            provider='vsts',
            external_id='vsts_external_id',
            name='fabrikam-fiber-inc.visualstudio.com',
            metadata={
                'domain_name': 'fabrikam-fiber-inc.visualstudio.com',
                'default_project': '0987654321',
            }
        )
        identity = Identity.objects.create(
            idp=IdentityProvider.objects.create(
                type='vsts',
                config={},
            ),
            user=self.user,
            external_id='vsts',
            data={
                'access_token': '123456789',
                'expires': time() + 1234567,
            }
        )
        model.add_organization(self.organization.id, identity.id)
        self.integration = VstsIntegration(model, self.organization.id)
        self.issue_id = 309

    @responses.activate
    def test_create_issue(self):
        responses.add(
            responses.PATCH,
            'https://fabrikam-fiber-inc.visualstudio.com/0987654321/_apis/wit/workitems/$Bug?api-version=3.0',
            body=WORK_ITEM_RESPONSE,
            content_type='application/json',
        )

        # group = self.create_group(message='Hello world', culprit='foo.bar')

        form_data = {
            'title': 'Hello',
            'description': 'Fix this.',
        }
        assert self.integration.create_issue(form_data) == {
            'key': self.issue_id,
            'description': 'Fix this.',
            'title': 'Hello',
        }
        request = responses.calls[-1].request
        assert request.headers['Content-Type'] == 'application/json-patch+json'
        payload = json.loads(request.body)
        assert payload == [
            {
                'op': 'add',
                'path': '/fields/System.Title',
                'value': 'Hello',
            },
            # Adds both a comment and a description.
            # See method for details.
            {
                'op': 'add',
                'path': '/fields/System.Description',
                'value': '<p>Fix this.</p>\n',
            },
            {
                'op': 'add',
                'path': '/fields/System.History',
                'value': '<p>Fix this.</p>\n',
            },
            # {
            #     "op": "add",
            #     "path": "/relations/-",
            #     "value": {
            #         "rel": "Hyperlink",
            #         "url": 'http://testserver/baz/bar/issues/1/',
            #     }
            # }
        ]

    @responses.activate
    def test_get_issue(self):
        responses.add(
            responses.GET,
            'https://fabrikam-fiber-inc.visualstudio.com/DefaultCollection/_apis/wit/workitems/%d' % self.issue_id,
            body=WORK_ITEM_RESPONSE,
            content_type='application/json',
        )
        assert self.integration.get_issue(self.issue_id) == {
            'key': self.issue_id,
            'description': 'Fix this.',
            'title': 'Hello',
        }
        request = responses.calls[-1].request
        assert request.headers['Content-Type'] == 'application/json'
