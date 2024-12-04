<template>
	<div class="container mx-auto p-4">
		<!-- Login Section -->
		<div class="flex justify-between items-center mb-4">
			<h1 class="text-2xl font-semibold">Movie Details</h1>
			<div>
				<button
					v-if="!isLoggedIn"
					@click="login"
					class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Login as Admin
				</button>
				<span v-else class="text-green-600">Logged in as Admin</span>
			</div>
		</div>

		<!-- Movie Details Section -->
		<div v-if="movie" class="flex">
			<!-- Movie Image -->
			<div class="w-1/3">
				<img
					:src="movie.poster_url || defaultPoster"
					alt="Movie Poster"
					class="w-full h-full object-contain rounded-lg shadow-lg"
				/>
			</div>

			<!-- Movie Details -->
			<div class="w-2/3 pl-6">
				<h1 class="text-4xl font-semibold mb-4">{{ movie.title }}</h1>
				<p class="text-xl mb-2">
					<strong>Year:</strong> {{ movie.year }}
				</p>
				<p class="text-xl mb-4">
					<strong>Director:</strong> {{ movie.director }}
				</p>
				<p class="text-lg mb-6">{{ movie.plot }}</p>

				<!-- IMDb Link -->
				<a
					v-if="movie.imdb_id"
					:href="imdbLink"
					target="_blank"
					class="text-blue-600 hover:underline"
				>
					View on IMDb
				</a>

				<!-- Delete and Update Buttons -->
				<div class="mt-6 flex space-x-4">
					<button
						@click="deleteMovie"
						class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
					>
						Delete Movie
					</button>
					<button
						@click="openUpdateModal"
						class="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
					>
						Update Movie
					</button>
				</div>
			</div>
		</div>

		<!-- Movie Not Found Message -->
		<div v-else-if="!loading && !movie">
			<h2 class="text-3xl text-red-600">Movie not found!</h2>
			<p class="text-lg text-gray-600">
				Sorry, the movie you're looking for does not exist.
			</p>
		</div>

		<!-- Loading Indicator -->
		<div v-if="loading" class="text-center text-xl text-gray-600">
			<p>Loading movie details...</p>
		</div>

		<!-- Update Modal -->
		<div
			v-if="showUpdateModal"
			class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
		>
			<div class="bg-white p-6 rounded-lg shadow-lg w-1/2">
				<h2 class="text-2xl font-semibold mb-4">Update Movie</h2>

				<form @submit.prevent="updateMovie">
					<div class="mb-4">
						<label for="title" class="block font-semibold mb-2"
							>Title:</label
						>
						<input
							v-model="updateData.title"
							type="text"
							id="title"
							class="w-full px-3 py-2 border rounded"
						/>
					</div>

					<div class="mb-4">
						<label for="year" class="block font-semibold mb-2"
							>Year:</label
						>
						<input
							v-model="updateData.year"
							type="number"
							id="year"
							class="w-full px-3 py-2 border rounded"
						/>
					</div>

					<div class="mb-4">
						<label for="director" class="block font-semibold mb-2"
							>Director:</label
						>
						<input
							v-model="updateData.director"
							type="text"
							id="director"
							class="w-full px-3 py-2 border rounded"
						/>
					</div>

					<div class="mb-4">
						<label for="plot" class="block font-semibold mb-2"
							>Plot:</label
						>
						<textarea
							v-model="updateData.plot"
							id="plot"
							class="w-full px-3 py-2 border rounded"
						></textarea>
					</div>

					<div class="flex justify-end space-x-4">
						<button
							@click="closeUpdateModal"
							type="button"
							class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
						>
							Cancel
						</button>
						<button
							type="submit"
							class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
						>
							Update
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiUrl } from '@/config'

export default {
	name: 'MovieDetails',
	setup() {
		const route = useRoute()
		const router = useRouter()
		const movieId = route.params.id
		const movie = ref(null)
		const loading = ref(true)
		const errorMessage = ref('')
		const isLoggedIn = ref(false)
		const adminToken = ref('')
		const showUpdateModal = ref(false)
		const updateData = ref({})

		const defaultPoster = '/images/no-poster-available.jpg'

		const imdbLink = computed(() => {
			return movie.value?.imdb_id
				? `https://www.imdb.com/title/${movie.value.imdb_id}`
				: ''
		})

		const fetchMovieDetails = async () => {
			try {
				loading.value = true
				const response = await fetch(`${apiUrl}/movies/${movieId}`)
				if (response.ok) {
					const data = await response.json()
					movie.value = data
					updateData.value = { ...data }
				} else {
					errorMessage.value = 'Movie not found!'
					movie.value = null
				}
			} catch (error) {
				errorMessage.value =
					'Error fetching movie details. Please try again later.'
				movie.value = null
			} finally {
				loading.value = false
			}
		}

		const login = () => {
			adminToken.value = 'token123'
			isLoggedIn.value = true
		}

		const deleteMovie = async () => {
			try {
				const response = await fetch(`${apiUrl}/movies/${movieId}`, {
					method: 'DELETE',
					headers: {
						Authorization: `Bearer ${adminToken.value}`,
					},
				})

				if (response.ok) {
					alert('Movie deleted successfully!')
					router.push('/')
				} else {
					const errorData = await response.json()
					alert(`Failed to delete movie: ${errorData.detail}`)
				}
			} catch (error) {
				console.error('Error deleting movie:', error)
				alert('An error occurred while deleting the movie.')
			}
		}

		const openUpdateModal = () => {
			showUpdateModal.value = true
		}

		const closeUpdateModal = () => {
			showUpdateModal.value = false
		}

		const updateMovie = async () => {
			try {
				const response = await fetch(`${apiUrl}/movies/${movieId}`, {
					method: 'PATCH',
					headers: {
						'Content-Type': 'application/json',
						Authorization: `Bearer ${adminToken.value}`,
					},
					body: JSON.stringify(updateData.value),
				})

				if (response.ok) {
					const updatedMovie = await response.json()
					movie.value = updatedMovie
					alert('Movie updated successfully!')
					closeUpdateModal()
				} else {
					const errorData = await response.json()
					alert(`Failed to update movie: ${errorData.detail}`)
				}
			} catch (error) {
				console.error('Error updating movie:', error)
				alert('An error occurred while updating the movie.')
			}
		}

		onMounted(fetchMovieDetails)

		return {
			movie,
			loading,
			errorMessage,
			defaultPoster,
			imdbLink,
			isLoggedIn,
			login,
			deleteMovie,
			showUpdateModal,
			openUpdateModal,
			closeUpdateModal,
			updateMovie,
			updateData,
		}
	},
}
</script>

<style scoped>
/* Add your custom styles if needed */
</style>
