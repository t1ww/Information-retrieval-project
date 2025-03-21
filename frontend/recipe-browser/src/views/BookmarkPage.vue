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
        const assignBookmarkToFolder = async (recipeId: string, folderName: string | number) => {
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

        // Remove a recipe from a folder using /folder_recipes DELETE
        const removeRecipeFromFolder = async (recipeId: string, folderName: string | number) => {
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;
                const response = await fetch("http://localhost:5000/folder_recipes", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: token,
                    },
                    credentials: "include",
                    body: JSON.stringify({ folder_name: folderName, recipe_id: recipeId }),
                });
                if (!response.ok) throw new Error("Failed to remove recipe from folder");

                // Optionally, refresh folders
                await fetchFolders(); // This will refresh the folders data
            } catch (error) {
                console.error("Error removing recipe from folder:", error);
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
            folderAssignment,
            removeRecipeFromFolder
        };
    },
});
</script>

<template>
    <div class="bookmark-page">
        <h1>Your Bookmarks</h1>

        <div v-if="isLoading" class="loading">Loading...</div>
        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

        <div v-if="bookmarks.length" class="recipe-list">
            <div v-for="bookmark in bookmarks" :key="bookmark.recipe_id" class="bookmark-item">
                <RecipeCard :recipe="bookmark" />
                <div class="bookmark-actions">
                    <button @click="removeBookmark(bookmark.recipe_id)" class="remove-btn">❌ Remove</button>
                    <div class="folder-assignment">
                        <select v-model="folderAssignment[bookmark.recipe_id]" class="folder-select">
                            <option disabled value="">Select Folder</option>
                            <option v-for="folder in Object.keys(folders)" :key="folder" :value="folder">
                                {{ folder }}
                            </option>
                        </select>
                        <button @click="assignBookmarkToFolder(bookmark.recipe_id, folderAssignment[bookmark.recipe_id])"
                            class="assign-btn">
                            ➕ Set Folder
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-else-if="!isLoading" class="empty-message">No bookmarks yet.</div>

        <section class="folders">
            <h3>Your Folders</h3>
            <div v-if="Object.keys(folders).length" class="folder-list">
                <div v-for="(recipes, folder) in folders" :key="folder" class="folder-card">
                    <h4>{{ folder }}</h4>
                    <div class="folder-recipes">
                        <div v-for="recipe in recipes" :key="recipe.recipe_id" class="folder-recipe-item">
                            <RecipeCard :recipe="recipe" />
                            <button @click="removeRecipeFromFolder(recipe.recipe_id, folder)" class="remove-folder-btn">
                                ❌ Remove
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="empty-message">No folders created yet.</div>

            <h3>Create a New Folder</h3>
            <div class="folder-creation">
                <input v-model="newFolderName" placeholder="Folder name" class="folder-input" />
                <button @click="createFolder" class="create-folder-btn">➕ Create</button>
            </div>
        </section>
    </div>
</template>

<style scoped>
/* Dark Theme Styles */
.bookmark-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: #121212; /* Dark background */
    color: #ffffff; /* White text */
}

h1, h3 {
    text-align: center;
    margin-bottom: 10px;
    color: #ffffff; /* Ensures headings are readable */
}

/* Loading & Error Messages */
.loading,
.error,
.empty-message {
    text-align: center;
    margin-top: 10px;
}

.error {
    color: #ff4d4d;
    font-weight: bold;
}

/* Recipe List */
.recipe-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}

.bookmark-item {
    background: #1e1e1e; /* Darker card background */
    color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 4px 6px rgba(255, 255, 255, 0.1); /* Softer shadow */
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.bookmark-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    width: 100%;
}

.remove-btn,
.remove-folder-btn {
    background: #b83a3a;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: 0.2s;
}

.remove-btn:hover,
.remove-folder-btn:hover {
    background: #ffabab;
}

/* Folder Assignment */
.folder-assignment {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;
}

.folder-select {
    flex: 1;
    padding: 6px;
    border-radius: 6px;
    border: 1px solid #555; /* Darker border */
    background: #1e1e1e;
    color: white;
}

.assign-btn {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: 0.2s;
}

.assign-btn:hover {
    background: #91ff96;
}

/* Folder Section */
.folders {
    margin-top: 30px;
}

.folder-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}

/* Folder Cards */
.folder-card {
    background: #1e1e1e; /* Darker background */
    color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 4px 6px rgba(255, 255, 255, 0.1);
}

.folder-card h4 {
    text-align: center;
    margin-bottom: 10px;
}

/* Folder Recipes */
.folder-recipes {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 10px;
}

.folder-recipe-item {
    background: #2a2a2a;
    color: white;
    padding: 10px;
    border-radius: 6px;
    box-shadow: 0px 2px 4px rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    flex-direction: column; /* Stack items vertically */
    justify-content: space-between;
}

/* Create Folder */
.folder-creation {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 10px;
}

.folder-input {
    padding: 8px;
    border: 1px solid #555;
    border-radius: 6px;
    background: #1e1e1e;
    color: white;
}

.create-folder-btn {
    background: #007BFF;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: 0.2s;
}

.create-folder-btn:hover {
    background: #86c0ff;
}
</style>
