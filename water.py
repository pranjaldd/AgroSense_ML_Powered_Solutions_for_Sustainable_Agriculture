from flask import Blueprint, render_template, request

# Define the Blueprint
cropwater_bp = Blueprint('cropwater_bp', __name__)

# Water Footprint Calculation Class
class AgricultureWaterFootprint:
    def __init__(self, crop, area, blue_cwr, green_cwr, pollution_load, irrigation_efficiency, growing_period):
        self.crop = crop
        self.area = area
        self.blue_cwr = blue_cwr
        self.green_cwr = green_cwr
        self.pollution_load = pollution_load
        self.irrigation_efficiency = irrigation_efficiency
        self.growing_period = growing_period

    def calculate_footprint(self):
        blue_footprint = self.blue_cwr * self.area * self.growing_period / 1000  # in cubic meters
        green_footprint = self.green_cwr * self.area * self.growing_period / 1000  # in cubic meters
        gray_footprint = self.pollution_load * self.area * self.growing_period / 1000  # in cubic meters
        total_footprint = blue_footprint + green_footprint + gray_footprint
        return {
            "crop": self.crop,
            "area": self.area,
            "Blue Water Footprint": blue_footprint,
            "Green Water Footprint": green_footprint,
            "Gray Water Footprint": gray_footprint,
            "Total Water Footprint": total_footprint
        }

# Route to Water Footprint Calculation Page
@cropwater_bp.route('/water_footprint', methods=['GET', 'POST'])
def water_footprint():
    if request.method == 'POST':
        crop = request.form['crop']
        area = float(request.form['area'])
        blue_cwr = float(request.form['blue_cwr'])
        green_cwr = float(request.form['green_cwr'])
        pollution_load = float(request.form['pollution_load'])
        irrigation_efficiency = float(request.form['irrigation_efficiency'])
        growing_period = int(request.form['growing_period'])

        # Create an instance of AgricultureWaterFootprint
        wf = AgricultureWaterFootprint(crop, area, blue_cwr, green_cwr, pollution_load,
                                       irrigation_efficiency, growing_period)
        # Get the footprint results
        result = wf.calculate_footprint()

        # Pass the result data to the water_result.html template
        return render_template('water_result.html', 
                               crop=result['crop'], 
                               area=result['area'],
                               blue_footprint=result['Blue Water Footprint'], 
                               green_footprint=result['Green Water Footprint'], 
                               gray_footprint=result['Gray Water Footprint'], 
                               total_footprint=result['Total Water Footprint'])
    return render_template('water_index.html')  # Display input form

@cropwater_bp.route('/water_index')
def water_index():
    return render_template('water_index.html')
