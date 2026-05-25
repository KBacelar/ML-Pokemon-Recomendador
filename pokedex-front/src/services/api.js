import axios from 'axios';

const POKEAPI_BASE = 'https://pokeapi.co/api/v2';

const BACKEND_BASE =
  process.env.REACT_APP_BACKEND_URL || 'http://localhost:3001';

export const pokeApi = axios.create({
  baseURL: POKEAPI_BASE,
  timeout: 10000,
});

export const backendApi = axios.create({
  baseURL: BACKEND_BASE,
  timeout: 10000,
});
