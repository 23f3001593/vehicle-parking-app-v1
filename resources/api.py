from flask_restful import Api
from .auth_api import LoginAPI, RegisterAPI
from .user_api import UserAPI, UserDashboardAPI, AdminDashboardAPI, RegisteredUsersAPI
from .parking_lot_api import ParkingLotAPI, OccupiedParkingSpotsAPI
from .reservation_api import ReservationBookAPI, ReservationReleaseAPI, UserReservationHistoryAPI, AdminReservationViewAPI

def create_api(app):
    api = Api(app)
    api.add_resource(LoginAPI, "/api/login")
    api.add_resource(RegisterAPI, "/api/register")
    api.add_resource(UserAPI, "/api/user/profile/<int:user_id>")
    api.add_resource(UserDashboardAPI, "/api/user/dashboard/<int:user_id>")
    api.add_resource(AdminDashboardAPI, "/api/admin/dashboard")
    api.add_resource(RegisteredUsersAPI, "/api/admin/registered-users")
    api.add_resource(ParkingLotAPI, "/api/parking-lot/new", "/api/parking-lot/<int:lot_id>")
    api.add_resource(OccupiedParkingSpotsAPI, "/api/parking-spot/occupied/<int:lot_id>")
    api.add_resource(ReservationBookAPI, "/api/reservation/book/<int:user_id>/<int:lot_id>")
    api.add_resource(ReservationReleaseAPI, "/api/reservation/release/<int:reservation_id>")
    api.add_resource(UserReservationHistoryAPI, "/api/user/history/<int:user_id>")
    api.add_resource(AdminReservationViewAPI, "/api/admin/reservations")