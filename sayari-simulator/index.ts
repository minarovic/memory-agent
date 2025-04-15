// deno-lint-ignore-file no-explicit-any

// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts"
/// <reference lib="deno.ns" />

// Načítání z Supabase Storage místo lokálních souborů
async function fetchMockData(fileName) {
  try {
    console.log(`Fetching mock data from Storage: ${fileName}`);
    const response = await fetch(`https://zyjgjpdwpdgfrpilxvvg.supabase.co/storage/v1/object/public/mock-data/${fileName}`);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    const data = await response.json();
    console.log(`Successfully fetched mock data for: ${fileName}`);
    return data;
  } catch (error) {
    console.error(`Error fetching mock data: ${error.message}`);
    throw new Error(`Failed to fetch mock data ${fileName}: ${error.message}`);
  }
}

// Ponechej původní funkci pro lokální vývoj
async function tryReadJsonFile(path) {
  try {
    console.log(`Attempting to read file from path: ${path}`);
    // @ts-ignore
    const text = await Deno.readTextFile(path);
    console.log(`Successfully read file with length: ${text.length} bytes`);
    return JSON.parse(text);
  } catch (error) {
    console.error(`Error reading file from ${path}: ${error.message}`);
    throw new Error(`Failed to read JSON file from ${path}: ${error.message}`);
  }
}

// Implementace simulátoru Sayari API
// @ts-ignore
Deno.serve(async (req) => {
  try {
    console.log("Starting request handling");
    // @ts-ignore
    console.log("Current directory:", Deno.cwd());
    
    const url = new URL(req.url);
    const path = url.pathname;
    const params = Object.fromEntries(url.searchParams);
    
    console.log(`Received request: ${path} with params:`, params);
    
    // Router pro různé endpointy
    if (path.includes('/search/entity')) {
      return handleEntitySearch(params);
    } 
    else if (path.match(/\/entity\/[^\/]+$/)) {
      const entityId = path.split('/').pop() || '';
      return handleEntityDetail(entityId, params);
    }
    else if (path.includes('/relationships')) {
      // Využijeme regulární výraz pro extrakci ID entity
      const matches = path.match(/\/entity\/([^\/]+)\/relationships/);
      const entityId = matches ? matches[1] : '';
      console.log(`Extracted entityId from path: ${entityId}`);
      return handleRelationships(entityId, params);
    }
    
    // Základní endpoint
    return new Response(
      JSON.stringify({ status: "OK", message: "Sayari API simulator is running!" }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error: any) {
    console.error("Error processing request:", error);
    return new Response(
      JSON.stringify({ error: error.message || "An unknown error occurred" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});

// Handler pro vyhledávání entit
async function handleEntitySearch(params) {
  try {
    // Nahrazení načtení souboru za načtení z Storage
    const mockData = await fetchMockData('entity_search.json');
    
    // Filtrování podle parametru q (query)
    let filteredData = mockData;
    if (params.q) {
      filteredData = { ...mockData };
      filteredData.data = mockData.data.filter(entity => 
        entity.label.toLowerCase().includes(params.q.toLowerCase())
      );
      filteredData.total = filteredData.data.length;
    }
    
    // Simulace paginace
    const offset = parseInt(params.offset || '0');
    const limit = parseInt(params.limit || '10');
    
    const paginatedData = {
      ...filteredData,
      limit: limit,
      offset: offset,
      data: filteredData.data.slice(offset, offset + limit),
      next: offset + limit < filteredData.data.length
    };
    
    return new Response(
      JSON.stringify(paginatedData),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error in entity search handler:", error);
    return new Response(
      JSON.stringify({ 
        error: "Failed to process entity search request", 
        details: error.message 
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

// Handler pro detail entity
async function handleEntityDetail(entityId, params) {
  try {
    // Nahrazení načtení souboru za načtení z Storage
    const mockData = await fetchMockData('entity_detail.json');
    
    // Hledáme entitu podle ID
    const entity = mockData.find(e => e.id === entityId);
    
    if (entity) {
      return new Response(
        JSON.stringify(entity),
        { headers: { "Content-Type": "application/json" } }
      );
    } else {
      return new Response(
        JSON.stringify({ error: "Entity not found", requested_id: entityId }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }
  } catch (error) {
    console.error("Error in entity detail handler:", error);
    return new Response(
      JSON.stringify({ 
        error: "Failed to process entity detail request", 
        details: error.message 
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

// Handler pro vztahy entity
async function handleRelationships(entityId, params) {
  try {
    console.log(`Handling relationships for entityId: "${entityId}"`);
    
    // Načtení dat ze Storage
    console.log("Fetching relationships.json from Storage...");
    const mockData = await fetchMockData('relationships.json');
    console.log(`Data fetched. Total relationships: ${mockData.relationships?.length || 0}`);
    
    // Kontrola datové struktury
    if (!mockData.relationships || !Array.isArray(mockData.relationships)) {
      console.error("Invalid data structure:", JSON.stringify(mockData).substring(0, 200));
      throw new Error("Invalid relationships data structure");
    }
    
    // Filtrování relací podle entityId
    let filteredRelations = mockData.relationships.filter(rel => 
      rel.from_id === entityId || rel.to_id === entityId
    );
    
    console.log(`Found ${filteredRelations.length} relationships matching entityId "${entityId}"`);
    
    if (filteredRelations.length > 0) {
      console.log("First matching relationship:", JSON.stringify(filteredRelations[0]));
    }
    
    // Filtrování podle typu vztahu, pokud je zadán
    if (params.type) {
      const types = params.type.split(',');
      console.log(`Filtering by types: ${types.join(', ')}`);
      filteredRelations = filteredRelations.filter(rel => types.includes(rel.type));
      console.log(`After type filtering: ${filteredRelations.length} relationships`);
    }
    
    // Připravení struktury odpovědi
    const response = {
      total: filteredRelations.length,
      limit: parseInt(params.limit || '20'),
      offset: parseInt(params.offset || '0'),
      relationships: filteredRelations,
      next: parseInt(params.limit || '20') + parseInt(params.offset || '0') < filteredRelations.length
    };
    
    // Implementace paginace
    response.relationships = filteredRelations.slice(
      parseInt(params.offset || '0'), 
      parseInt(params.offset || '0') + parseInt(params.limit || '20')
    );
    
    console.log(`Returning ${response.relationships.length} relationships`);
    
    return new Response(
      JSON.stringify(response),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error(`Error processing relationships:`, error);
    return new Response(
      JSON.stringify({ 
        error: "Failed to process relationships request", 
        details: error.message 
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

console.log("Sayari API simulator started");