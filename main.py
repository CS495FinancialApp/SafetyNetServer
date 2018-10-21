#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import endpoints
import webapp2
import braintree
import xml.etree.ElementTree as ET
from protorpc.messages import StringField
from protorpc import messages
from protorpc import message_types
from protorpc import remote

class Data(messages.Message):
    """Data that stores a message"""
    content = messages.StringField(1)  # type: StringField


@endpoints.api(name='payments', version='v2')
class PaymentApi(remote.Service):

    def __init__(self):
        ids = ET.parse('server_ids.xml')
        root = ids.getroot()

        global gateway
        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment='sandbox',
                merchant_id=root.find('merchantId').text,
                public_key=root.find('publicKey').text,
                private_key=root.find('privateKey').text))

    @endpoints.method(
        # This method does not take a request message.
        message_types.VoidMessage,
        # This method returns a Data message.
        Data,
        path='hello',
        http_method='GET',
        name='hello.show')
    def show_hello(self,unused_request):
        return Data(content="Hello World!")

    # ResourceContainers are used to encapsuate a request body and url
    # parameters. This one is used to represent the Greeting ID for the
    # greeting_get method.
    TOKEN_RESOURCE = endpoints.ResourceContainer(
        # The request body should be empty.
        message_types.VoidMessage,
        # Accept one url parameter: an string named 'id'
        userid=messages.StringField(1, variant=messages.Variant.STRING))

    @endpoints.method(
        # Use the ResourceContainer defined above to accept an empty body
        # but an ID in the query string.
        TOKEN_RESOURCE,
        # This method returns a Greeting message.
        Data,
        # The path defines the source of the URL parameter 'id'. If not
        # specified here, it would need to be in the query string.
        path='client_token/{userid}',
        http_method='GET',
        name='clienttoken.get')
    def get_clienttoken(self, request):
        client_token = gateway.client_token.generate({
            "customerId": request.userid
        })


api = endpoints.api_server([PaymentApi])
netstat