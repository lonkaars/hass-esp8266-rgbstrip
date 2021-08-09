import { AccessoryConfig, AccessoryPlugin, API, Logger, Service } from 'homebridge';
import axios from 'axios';
const Color = require('color');

export default class ESP8266RGBStrip implements AccessoryPlugin {
	private infoService: Service;
	private bulbService: Service;
	private state: {
		on: boolean;
		brightness: number;
		saturation: number;
		hue: number;
	};

	public name: string;
	public host: string;

	constructor(
		public readonly log: Logger,
		public readonly config: AccessoryConfig,
		public readonly api: API,
	) {
		this.name = config.name;
		this.host = config.host;
		this.state = {
			on: false,
			brightness: 100,
			saturation: 0,
			hue: 0,
		};

		this.infoService = new this.api.hap.Service.AccessoryInformation()
			.setCharacteristic(this.api.hap.Characteristic.Manufacturer, 'nodemcu')
			.setCharacteristic(this.api.hap.Characteristic.Model, 'esp8266');

		this.bulbService = new this.api.hap.Service.Lightbulb('White');
		this.registerServices();
	}

	registerServices() {
		this.bulbService.getCharacteristic(this.api.hap.Characteristic.On)
			.onGet(() => this.state.on)
			.onSet((on: boolean) => {
				this.state.on = on;
				this.updateLamp();
			});
		this.bulbService.getCharacteristic(this.api.hap.Characteristic.Brightness)
			.onGet(() => this.state.brightness)
			.onSet((brt: number) => {
				this.state.brightness = brt;
				this.updateLamp();
			});
		this.bulbService.getCharacteristic(this.api.hap.Characteristic.Hue)
			.onGet(() => this.state.hue)
			.onSet((hue: number) => {
				this.state.hue = hue;
				this.updateLamp();
			});
		this.bulbService.getCharacteristic(this.api.hap.Characteristic.Saturation)
			.onGet(() => this.state.saturation)
			.onSet((sat: number) => {
				this.state.saturation = sat;
				this.updateLamp();
			});
	}

	updateLamp() {
		var rgb = Color({ h: this.state.hue, s: this.state.saturation, v: Number(this.state.on && this.state.brightness) });
		var color = [rgb.red(), rgb.green(), rgb.blue()].map(i => i.toString(16).padStart(2, '0')).join('');
		axios.post("http://" + this.host, color);
	}

	getServices() {
		return [
			this.infoService,
			this.bulbService,
		];
	}
}

module.exports = (api: API) => { api.registerAccessory('ESP8266RGBStrip', ESP8266RGBStrip) };
