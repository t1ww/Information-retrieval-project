<script lang="ts">
import { defineComponent, ref, onMounted, reactive } from "vue";
import RecipeCard from "@/components/RecipeCard.vue";

interface Recipe {
    recipe_id: string;
    name: string;
    snippet: string;
    image_urls: string[];
    rating?: number;
}

export default defineComponent({
    name: "BookmarkPage",
    components: { RecipeCard },
    setup() {
        const bookmarks = ref<Recipe[]>([]);
        const folders = ref<{ [key: string]: Recipe[] }>({});
        const isLoading = ref<boolean>(true);
        const errorMessage = ref<string | null>(null);
        const newFolderName = ref<string>("");

        // This will store the selected folder for each bookmark by recipe_id
        const folderAssignment = reactive<{ [recipeId: string]: string }>({});

        // Fetch bookmarks from /user_bookmarks endpoint
        const fetchBookmarks = async () => {
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;
                const response = await fetch("http://localhost:5000/user_bookmarks", {
                    method: "GET",
                    headers: { Authorization: token },
                    credentials: "include",
                });
                if (!response.ok) throw new Error("Failed to fetch bookmarks");
                const data = await response.json();
                const recipeDetails = await Promise.all(
                    data.bookmarks.map(async (bookmark: any) => {
                        const recipeResponse = await fetch(`http://localhost:5000/recipe/${bookmark.recipe_id}`, {
                            headers: { Authorization: token },
                            credentials: "include",
                        });
                        if (!recipeResponse.ok) return null;
                        const recipeData = await recipeResponse.json();
                        // Initialize folder assignment for this bookmark (if not already set)
                        if (!folderAssignment[recipeData.recipe_id]) {
                            folderAssignment[recipeData.recipe_id] = "";
                        }
                        return {
                            ...recipeData,
                            rating: bookmark.rating,
                        };
                    })
                );
                bookmarks.value = recipeDetails.filter(Boolean);
            } catch (error) {
                errorMessage.value = (error as Error).message;
            } finally {
                isLoading.value = false;
            }
        };

        // Fetch folders from /folders endpoint
        const fetchFolders = async () => {
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;
                const response = await fetch("http://localhost:5000/folders", {
                    method: "GET",
                    headers: { Authorization: token },
                    credentials: "include",
                });
                if (!response.ok) throw new Error("Failed to fetch folders");
                const data = await response.json();
                const folderData: { [key: string]: Recipe[] } = {};
                for (const folderName in data) {
                    if (!Array.isArray(data[folderName])) {
                        console.error(`Expected an array for folder ${folderName}, got:`, data[folderName]);
                        continue;
                    }
                    const recipeDetails = await Promise.all(
                        data[folderName].map(async (recipeId: number) => {
                            const recipeResponse = await fetch(`http://localhost:5000/recipe/${recipeId}`, {
                                headers: { Authorization: token },
                                credentials: "include",
                            });
                            if (!recipeResponse.ok) return null;
                            const recipeData = await recipeResponse.json();
                            return {
                                ...recipeData,
                            };
                        })
                    );
                    folderData[folderName] = recipeDetails.filter(Boolean);
                }
                folders.value = folderData;
            } catch (error) {
                console.error("Error fetching folders:", error);
            }
        };

        // Remove a bookmark using /bookmark DELETE
        const removeBookmark = async (recipeId: string) => {
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;
                const response = await fetch("http://localhost:5000/bookmark", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: token,
                    },
                    credentials: "include",
                    body: JSON.stringify({ recipe_id: recipeId }),
                });
                if (!response.ok) throw new Error("Failed to remove bookmark");
                bookmarks.value = bookmarks.value.filter(b => b.recipe_id !== recipeId);
            } catch (error) {
                console.error("Error removing bookmark:", error);
            }
        };

        // Create a new folder using /folders POST
        const createFolder = async () => {
            if (!newFolderName.value.trim()) return;
            const token = localStorage.getItem("authToken");
            if (!token) return;
            const response = await fetch("http://localhost:5000/folders", {
                method: "POST",
                headers: { "Content-Type": "application/json", Authorization: token },
                credentials: "include",
                body: JSON.stringify({ folder_name: newFolderName.value }),
            });
            if (!response.ok) {
                errorMessage.value = "Failed to create folder";
                return;
            }
            newFolderName.value = "";
            fetchFolders();
        };

        // Assign a bookmark to a folder using /folder_recipes POST endpoint
        const assignBookmarkToFolder = async (recipeId: string, folderName: string) => {
            if (!folderName) {
                console.error("No folder selected for recipe", recipeId);
                return;
            }
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;
                const response = await fetch("http://localhost:5000/folder_recipes", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", Authorization: token },
                    credentials: "include",
                    body: JSON.stringify({ folder_name: folderName, recipe_id: recipeId }),
                });
                if (!response.ok) throw new Error("Failed to assign bookmark to folder");
                // Optionally, refresh folders
                await fetchFolders();
            } catch (error) {
                console.error("Error assigning bookmark to folder:", error);
            }
        };

        onMounted(async () => {
            await fetchBookmarks();
            await fetchFolders();
        });

        return {
            bookmarks,
            folders,
            isLoading,
            errorMessage,
            removeBookmark,
            newFolderName,
            createFolder,
            assignBookmarkToFolder,
            folderAssignment
        };
    },
});
</script>


<template>
    <div class="bookmark-page">
        <h1>Your Bookmarks</h1>
        <div v-if="isLoading">Loading...</div>
        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
        <div v-if="bookmarks.length" class="recipe-list">
            <div v-for="bookmark in bookmarks" :key="bookmark.recipe_id" class="bookmark-item">
                <RecipeCard :recipe="bookmark" />
                <button @click="removeBookmark(bookmark.recipe_id)">❌ Remove</button>
                <!-- Folder assignment UI -->
                <div class="folder-assignment">
                    <select v-model="folderAssignment[bookmark.recipe_id]">
                        <option disabled value="">Select Folder</option>
                        <option v-for="folder in Object.keys(folders)" :key="folder" :value="folder">
                            {{ folder }}
                        </option>
                    </select>
                    <button @click="assignBookmarkToFolder(bookmark.recipe_id, folderAssignment[bookmark.recipe_id])">
                        Set Folder
                    </button>
                </div>
            </div>
        </div>
        <div v-else-if="!isLoading">No bookmarks yet.</div>
        <section class="folders">
            <h3>Your Folders</h3>
            <div v-if="Object.keys(folders).length">
                <div v-for="(recipes, folder) in folders" :key="folder">
                    <h4>{{ folder }}</h4>
                    <div class="recipe-list">
                        <RecipeCard
                            v-for="recipe in recipes"
                            :key="recipe.recipe_id"
                            :recipe="recipe"
                        />
                    </div>
                </div>
            </div>
            <div v-else>No folders created yet.</div>
            <h3>Create a New Folder</h3>
            <input v-model="newFolderName" placeholder="Folder name" />
            <button @click="createFolder">➕ Create</button>
        </section>
    </div>
</template>

<style scoped>
.recipe-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}
.bookmark-item {
    border: 1px solid #ccc;
    padding: 10px;
}
.folder-assignment {
    margin-top: 10px;
}
.folders {
    margin-top: 30px;
}
.error {
    color: red;
}
</style>
