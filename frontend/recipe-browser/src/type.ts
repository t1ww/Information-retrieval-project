export interface RecipeDetailed {
    recipe_id: string;
    name: string;
    description: string;
    snippet: string;
    ingredients: [string, string][];
    instructions: string[];
    image_urls: string[];
    author_name: string;
    calories: number;
    carbohydrate_content: number;
    cholesterol_content: number;
    cook_time: string;
    fat_content: number;
    fiber_content: number;
    protein_content: number;
    recipe_category: string;
    recipe_servings: number;
    sugar_content: number;
    prep_time: string;
    total_time: string;
    keywords: string[];
}

export interface Recipe {
    recipe_id: string;
    name: string;
    snippet: string;
    image_urls: string[];
    rating?: number;
}