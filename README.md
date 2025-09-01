# Offroad Trip Planner API

A comprehensive offroad trip planning system that includes late-night trip planning, spontaneous trip suggestions, offroad guides, and mechanic assistance.

## Features

- **Late-Night Trip Planning**: Get customized plans for night-time offroad adventures
- **Spontaneous Trips**: Quick planning for last-minute offroad getaways
- **Offroad Guide**: Access to expert tips and best practices
- **Vehicle Maintenance**: Pre and post-trip checklists
- **Mechanic Assistant**: Quick solutions for common offroad vehicle issues

## Setup

1. Clone the repository

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python app.py
   ```

4. The API will be available at `http://localhost:5000`

## API Endpoints

### Get the Complete Offroad Guide

- **GET** `/api/guide`

### Get a Random Offroad Tip

- **GET** `/api/tips/random`
  - Returns a random tip from a random category.

### Plan a Late-Night Trip

- **POST** `/api/plan/late-night`
  - Request body: `{ "destination": "Your Destination" }`

### Plan a Spontaneous Trip

- **POST** `/api/plan/spontaneous`
  - Request body: `{ "duration_hours": 4 }`

### Get Vehicle Checklist

- **GET** `/api/vehicle/checklist`

### Anticipate Maintenance Needs

- **POST** `/api/maintenance/anticipate`
  - Request body: `{ "trip_type": "desert", "mileage": 50000 }`

### Get Mechanic Assistance

- **POST** `/api/mechanic/assist`
  - Request body: `{ "issue": "flat tire" }`
  - Returns a detailed solution with tools, steps, and follow-up advice.

## Environment Variables

Create a `.env` file in the root directory with any required environment variables.

## License

MIT
