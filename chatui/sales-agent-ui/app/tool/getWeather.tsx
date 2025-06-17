import { makeAssistantTool, makeHumanTool } from "@assistant-ui/react";
import { z } from "zod";
// Define the tool
const weatherTool = makeHumanTool({
  description: "Get current weather for a location",
  parameters: z.object({
    location: z.string().describe("City name or zip code"),
    unit: z.enum(["celsius", "fahrenheit"]).default("celsius")
  }),
  execute: async ({ location, unit }: { location: string; unit?: "celsius" | "fahrenheit" }) => {
    // Tool execution logic
    const weather = await fetchWeatherAPI(location, unit);
    return weather;
  }
});

interface WeatherData {

  location: string;

  temperature: number;

  unit: string;

  condition: string;

}


function fetchWeatherAPI(location: string, unit: string = 'celsius'): Promise<WeatherData> {

  return new Promise((resolve) => {

    // 模拟API延迟

    setTimeout(() => {

      // 模拟天气数据

      const mockWeatherData: WeatherData = {

        location: location,

        temperature: Math.floor(Math.random() * 30) + 1, // 随机温度 1-30

        unit: unit,

        condition: ['Sunny', 'Cloudy', 'Rainy', 'Snowy'][Math.floor(Math.random() * 4)] // 随机天气状况

      };


      resolve(mockWeatherData);

    }, 1000); // 模拟1秒的延迟

  });

}

// Create the component
export const WeatherTool = makeAssistantTool(weatherTool);
import { makeAssistantTool, makeHumanTool } from "@assistant-ui/react";
import { z } from "zod";
// Define the tool
const weatherTool = makeHumanTool({
  description: "Get current weather for a location",
  parameters: z.object({
    location: z.string().describe("City name or zip code"),
    unit: z.enum(["celsius", "fahrenheit"]).default("celsius")
  }),
  execute: async ({ location, unit }: { location: string; unit?: "celsius" | "fahrenheit" }) => {
    // Tool execution logic
    const weather = await fetchWeatherAPI(location, unit);
    return weather;
  }
});

interface WeatherData {

  location: string;

  temperature: number;

  unit: string;

  condition: string;

}


function fetchWeatherAPI(location: string, unit: string = 'celsius'): Promise<WeatherData> {

  return new Promise((resolve) => {

    // 模拟API延迟

    setTimeout(() => {

      // 模拟天气数据

      const mockWeatherData: WeatherData = {

        location: location,

        temperature: Math.floor(Math.random() * 30) + 1, // 随机温度 1-30

        unit: unit,

        condition: ['Sunny', 'Cloudy', 'Rainy', 'Snowy'][Math.floor(Math.random() * 4)] // 随机天气状况

      };


      resolve(mockWeatherData);

    }, 1000); // 模拟1秒的延迟

  });

}

// Create the component
export const WeatherTool = makeAssistantTool(weatherTool);
import { makeAssistantTool, makeHumanTool } from "@assistant-ui/react";
import { z } from "zod";
// Define the tool
const weatherTool = makeHumanTool({
  description: "Get current weather for a location",
  parameters: z.object({
    location: z.string().describe("City name or zip code"),
    unit: z.enum(["celsius", "fahrenheit"]).default("celsius")
  }),
  execute: async ({ location, unit }: { location: string; unit?: "celsius" | "fahrenheit" }) => {
    // Tool execution logic
    const weather = await fetchWeatherAPI(location, unit);
    return weather;
  }
});

interface WeatherData {

  location: string;

  temperature: number;

  unit: string;

  condition: string;

}


function fetchWeatherAPI(location: string, unit: string = 'celsius'): Promise<WeatherData> {

  return new Promise((resolve) => {

    // 模拟API延迟

    setTimeout(() => {

      // 模拟天气数据

      const mockWeatherData: WeatherData = {

        location: location,

        temperature: Math.floor(Math.random() * 30) + 1, // 随机温度 1-30

        unit: unit,

        condition: ['Sunny', 'Cloudy', 'Rainy', 'Snowy'][Math.floor(Math.random() * 4)] // 随机天气状况

      };


      resolve(mockWeatherData);

    }, 1000); // 模拟1秒的延迟

  });

}

// Create the component
export const WeatherTool = makeAssistantTool(weatherTool);
