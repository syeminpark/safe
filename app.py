# app.py

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from interface import AddressForm
from googleAPI import addressToCoordinates, getStreetView
from TEJapanAPI import find_and_download_flood_data
from preprocessNCFile import openClosestFile, getNearestValueByCoordinates, floodVolumeProxy
from constants import TEJapanFileType
from datetime import datetime

def handle_form(data):
    try:
        # 1) Build the address
        address = " ".join([
            data["prefecture"],
            data["city"],
            data["town"],
            data["address2"]
        ])

        # 2) Geocode
        coords = addressToCoordinates(address)  # e.g. "35.78,139.90"

        # 3) Parse date+hour into a full datetime
        dt_str = f"{data['date']} {data['time']}"
        target_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

        # 4) Fetch Street‑View
        tiles, metas = getStreetView(
            coords,
            target_date=data["date"],
            mode=data["mode"]
        )
        w.set_street_images(tiles, metas)

        # 5) Download the best flood data for that datetime
        dt_fetched, resolution = find_and_download_flood_data(target_dt)
    

        # 6) Depth: open closest file before or at target_dt
        ds_depth = openClosestFile(
            TEJapanFileType.DEPTH,
            target_dt
        )
        depth_value, depth_time = getNearestValueByCoordinates(
            ds_depth,
            coords,
            target_dt
        )
   

        # 7) Fraction: open closest fraction file
        ds_frac = openClosestFile(
            TEJapanFileType.FRACTION,
            target_dt
        )
        frac_value, frac_time = getNearestValueByCoordinates(
            ds_frac,
            coords,
            target_dt
        )

        # 8) Compute and log volume proxy
        volume = floodVolumeProxy(depth_value, frac_value)


    except Exception as e:
        msg = str(e)
        w.log.append(f"⚠ Error: {msg}")
        QMessageBox.warning(w, "Error", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AddressForm()
    w.data_submitted.connect(handle_form)
    w.show()
    sys.exit(app.exec_())
