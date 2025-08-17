from js import window
from pyodide.ffi import create_proxy, to_js

from cj12.methods import KeyReceiveCallback


class LocationMethod:
    byte = 0x03
    static_id = "location"
    name = "Location"
    description = "A physical location"

    on_key_received: KeyReceiveCallback | None = None

    async def setup(self) -> None:
        self._map = None
        self._rect = None

        m = window.L.map("map").setView(to_js([0, 0]), 1)
        self._map = m

        layer_url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer_opts = {
            "maxZoom": 19,
            "attribution": '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }
        window.L.tileLayer(layer_url, layer_opts).addTo(m)

        async def on_click(e: object) -> None:
            lat = float(e.latlng.lat)  # pyright: ignore[reportAttributeAccessIssue]
            lng = float(e.latlng.lng)  # pyright: ignore[reportAttributeAccessIssue]

            rlat = round(lat, 3)
            rlng = round(lng, 3)
            key_str = f"{rlat:.4f},{rlng:.4f}"

            cell_half = 0.0005
            lat_min = rlat - cell_half
            lat_max = rlat + cell_half
            lng_min = rlng - cell_half
            lng_max = rlng + cell_half
            bounds = to_js([[lat_min, lng_min], [lat_max, lng_max]])

            if self._rect is None:
                self._rect = window.L.rectangle(
                    bounds,
                    {
                        "color": "#3388ff",
                        "weight": 1,
                        "fillOpacity": 0.1,
                        "interactive": False,
                    },
                ).addTo(m)
            else:
                self._rect.setBounds(bounds)

            if self.on_key_received is not None:
                await self.on_key_received(key_str.encode())

        m.on("click", create_proxy(on_click))
