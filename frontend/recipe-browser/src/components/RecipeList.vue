<script lang="ts">
import { defineComponent } from "vue";
import RecipeCard from "@/components/RecipeCard.vue";
import type { Recipe } from "@/type";

export default defineComponent({
    name: "RecipeList",
    components: {
        RecipeCard,
    },
    props: {
        recipes: {
            type: Array as () => Recipe[],
            required: true,
        },
    },
});
</script>

<template>
    <div v-if="recipes.length" class="recipe-list">
        <RecipeCard v-for="recipe in recipes" :key="recipe.recipe_id" :recipe="recipe" />
    </div>
    <div v-else>No recipes found.</div>
</template>

<style scoped>
.recipe-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16em, 1fr));
    gap: 0.5em;
}

</style>
