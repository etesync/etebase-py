# Copyright © 2017 Tom Hacohen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, version 3.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

class HttpException(Exception):
    pass


class UnauthorizedException(HttpException):
    pass


class UserInactiveException(HttpException):
    pass


class ServiceUnavailableException(HttpException):
    pass


class HttpNotFound(HttpException):
    pass


class VersionTooNew(Exception):
    pass


class SecurityException(Exception):
    pass


class IntegrityException(SecurityException):
    pass


class StorageException(Exception):
    pass


class DoesNotExist(StorageException):
    pass


class AlreadyExists(StorageException):
    pass


class TypeMismatch(StorageException):
    pass
