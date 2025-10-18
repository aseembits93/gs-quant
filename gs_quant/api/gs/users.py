"""
Copyright 2019 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from typing import List, Any, Dict

from pydash import get

from gs_quant.session import GsSession
from gs_quant.target.reports import User


class GsUsersApi:
    @classmethod
    def get_users(cls,
                  user_ids: List[str] = None,
                  user_emails: List[str] = None,
                  user_names: List[str] = None,
                  user_companies: List[str] = None,
                  limit: int = 100,
                  offset: int = 0) -> List:
        params = []
        if user_ids:
            params.append('id=' + '&id='.join(user_ids))
        if user_emails:
            params.append('email=' + '&email='.join(user_emails))
        if user_names:
            params.append('name=' + '&name='.join(user_names))
        if user_companies:
            params.append('company=' + '&company='.join(user_companies))
        params.append(f'limit={limit}')
        params.append(f'offset={offset}')
        url = '/users?' + '&'.join(params)
        return GsSession.current._get(url, cls=User)['results']

    @classmethod
    def get_my_guid(cls) -> str:
        return f"guid:{GsSession.current._get('/users/self')['id']}"

    @classmethod
    def get_current_user_info(cls) -> Dict[str, Any]:
        """
        Gets user
        :return: user
        """
        return GsSession.current._get('/users/self')

    @classmethod
    def get_current_app_managers(cls) -> List[str]:
        return [f"guid:{manager}" for manager in get(GsSession.current._get('/users/self'), 'appManagers', [])]
