<template>
	<div class="container mx-auto p-4">
		<!-- Search Bar and Add Movie Button -->
		<div class="mb-4 flex items-center justify-between">
			<div class="flex-1 md:flex md:items-center">
				<input
					type="text"
					v-model="searchQuery"
					@input="handleSearchInput"
					class="px-4 py-2 rounded border border-gray-300 w-full md:w-1/2"
					placeholder="Search for a movie..."
					aria-label="Search for a movie"
				/>
			</div>
			<!-- Add New Movie Button -->
			<router-link to="/add-movie">
				<button
					class="ml-4 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
				>
					Add New Movie
				</button>
			</router-link>
		</div>

		<!-- Movie Grid -->
		<div
			v-if="movies.length > 0"
			class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
		>
			<router-link
				v-for="movie in movies"
				:key="movie.id"
				:to="{ name: 'MovieDetails', params: { id: movie.id } }"
				class="bg-white rounded-lg shadow-lg overflow-hidden transform transition-transform duration-200 hover:scale-105"
			>
				<img
					:src="movie.poster_url || '/images/no-poster-available.jpg'"
					:alt="`Poster for ${movie.title}`"
					class="w-full h-64 object-cover"
				/>
				<div class="p-4">
					<h3 class="text-lg font-semibold">{{ movie.title }}</h3>
					<p class="text-sm text-gray-500">{{ movie.year }}</p>
				</div>
			</router-link>
		</div>

		<!-- No Movies Found -->
		<div v-else class="col-span-4 text-center text-lg text-gray-500">
			<p class="font-semibold text-2xl text-red-500">No movies found</p>
			<p class="text-sm text-gray-400">
				Try searching with a different title.
			</p>
		</div>

		<!-- Pagination and Limit Selector -->
		<div class="mt-4 flex justify-between items-center">
			<!-- Limit Selector -->
			<div class="flex items-center">
				<label for="limit" class="mr-2 text-lg">Movies per page:</label>
				<select
					id="limit"
					v-model.number="limit"
					@change="fetchMovies"
					class="px-4 py-2 border rounded-md"
					aria-label="Select movies per page"
				>
					<option
						v-for="value in pageSizeOptions"
						:key="value"
						:value="value"
					>
						{{ value }}
					</option>
				</select>
			</div>

			<!-- Pagination -->
			<div class="flex space-x-4">
				<button
					@click="changePage(currentPage - 1)"
					:disabled="currentPage <= 1"
					class="px-4 py-2 bg-blue-500 text-white rounded-md transition duration-200 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
					aria-label="Previous Page"
				>
					Previous
				</button>
				<span class="flex items-center text-lg">
					Page {{ currentPage }} of {{ totalPages }}
				</span>
				<button
					@click="changePage(currentPage + 1)"
					:disabled="currentPage >= totalPages"
					class="px-4 py-2 bg-blue-500 text-white rounded-md transition duration-200 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
					aria-label="Next Page"
				>
					Next
				</button>
			</div>
		</div>
	</div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { apiUrl } from '@/config'

export default {
	name: 'MoviesList',
	setup() {
		// State
		const movies = ref([])
		const searchQuery = ref('')
		const currentPage = ref(1)
		const totalPages = ref(1)
		const limit = ref(10) // Properly defined
		const errorMessage = ref('')
		const pageSizeOptions = ref([10, 20, 30]) // Use ref for options

		// Fetch movies
		const fetchMovies = async () => {
			errorMessage.value = ''
			try {
				const url = `${apiUrl}/movies/?page=${currentPage.value}&limit=${limit.value}`
				const response = await fetch(url)
				if (!response.ok) throw new Error('Failed to fetch movies')
				const data = await response.json()
				movies.value = data.movies
				totalPages.value = data.total_pages || 1
			} catch (error) {
				console.error(error)
				movies.value = []
				errorMessage.value = 'An error occurred while fetching movies.'
			}
		}

		// Search movies
		const searchMovies = async () => {
			errorMessage.value = ''
			if (!searchQuery.value) {
				// If the search query is empty, load movies normally
				currentPage.value = 1
				return fetchMovies()
			}

			try {
				const url = `${apiUrl}/movies/search?title=${encodeURIComponent(
					searchQuery.value
				)}`
				const response = await fetch(url)

				if (!response.ok) {
					// Handle HTTP errors
					if (response.status === 404) {
						movies.value = []
						totalPages.value = 1
						return
					}
					throw new Error('Failed to fetch search results')
				}

				// Update the movies state with the search results
				const data = await response.json()

				if (Array.isArray(data)) {
					movies.value = data // Assign the array directly to `movies`
					totalPages.value = 1 // Search results likely won't support pagination
				} else {
					movies.value = []
					errorMessage.value =
						'Unexpected data format from the server.'
				}
			} catch (error) {
				console.error(error)
				movies.value = []
				errorMessage.value =
					'An error occurred while searching for movies.'
			}
		}

		// Event handlers
		const changePage = (page) => {
			if (page > 0 && page <= totalPages.value) {
				currentPage.value = page
				fetchMovies()
			}
		}

		const handleSearchInput = () => {
			currentPage.value = 1
			searchMovies()
		}

		// Load movies on mount
		onMounted(fetchMovies)

		// Expose to template
		return {
			movies,
			searchQuery,
			currentPage,
			totalPages,
			limit,
			pageSizeOptions,
			errorMessage,
			changePage,
			fetchMovies,
			handleSearchInput,
		}
	},
}
</script>
