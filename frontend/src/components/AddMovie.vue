<template>
	<div class="container mx-auto p-4">
		<h1 class="text-2xl font-semibold mb-4">Add a New Movie</h1>
		<div class="space-y-4">
			<!-- Search Movie Section -->
			<div>
				<h2 class="text-xl">Search for Movie by Title</h2>
				<input
					v-model="searchTitle"
					type="text"
					placeholder="Enter movie title"
					class="px-4 py-2 rounded border border-gray-300 w-full"
				/>
				<button
					@click="searchAndCreate"
					class="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
				>
					Search and Add Movie
				</button>
			</div>

			<!-- Or fill in movie data manually -->
			<div>
				<h2 class="text-xl">Or Add Movie Details Manually</h2>
				<form @submit.prevent="submitMovieForm">
					<!-- Title -->
					<input
						v-model="movieForm.title"
						type="text"
						placeholder="Movie Title"
						:class="{ 'border-red-500': errorFields.title }"
						required
						class="px-4 py-2 rounded border w-full mb-2"
					/>
					<span
						v-if="errorFields.title"
						class="text-red-500 text-sm"
						>{{ errorMessages.title }}</span
					>

					<!-- IMDb ID -->
					<input
						v-model="movieForm.imdb_id"
						type="text"
						placeholder="IMDb ID (e.g., tt1375666)"
						:class="{ 'border-red-500': errorFields.imdb_id }"
						required
						class="px-4 py-2 rounded border w-full mb-2"
					/>
					<span
						v-if="errorFields.imdb_id"
						class="text-red-500 text-sm"
						>{{ errorMessages.imdb_id }}</span
					>

					<!-- Year -->
					<input
						v-model="movieForm.year"
						type="number"
						placeholder="Year"
						:class="{ 'border-red-500': errorFields.year }"
						class="px-4 py-2 rounded border w-full mb-2"
					/>
					<span
						v-if="errorFields.year"
						class="text-red-500 text-sm"
						>{{ errorMessages.year }}</span
					>

					<!-- Type (movie, series, episode) -->
					<input
						v-model="movieForm.type"
						type="text"
						placeholder="Type (e.g., movie, series, episode)"
						class="px-4 py-2 rounded border w-full mb-2"
					/>

					<!-- Poster URL -->
					<input
						v-model="movieForm.poster_url"
						type="text"
						placeholder="Poster URL"
						class="px-4 py-2 rounded border w-full mb-2"
					/>

					<!-- Genre -->
					<input
						v-model="movieForm.genre"
						type="text"
						placeholder="Genre (e.g., Action, Sci-Fi)"
						class="px-4 py-2 rounded border w-full mb-2"
					/>

					<!-- Director -->
					<input
						v-model="movieForm.director"
						type="text"
						placeholder="Director"
						class="px-4 py-2 rounded border w-full mb-2"
					/>

					<!-- Plot -->
					<textarea
						v-model="movieForm.plot"
						placeholder="Plot"
						class="px-4 py-2 rounded border w-full mb-2"
					></textarea>

					<!-- Submit Button -->
					<button
						type="submit"
						class="mt-2 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
					>
						Add Movie
					</button>
				</form>
			</div>
		</div>
	</div>
</template>

<script>
import { ref } from 'vue'
import { apiUrl } from '@/config'

export default {
	name: 'AddMovie',
	setup() {
		// Form state
		const searchTitle = ref('')
		const movieForm = ref({
			title: '',
			imdb_id: '',
			year: '',
			type: '',
			poster_url: '',
			genre: '',
			director: '',
			plot: '',
		})

		// Error state for each field
		const errorFields = ref({
			title: false,
			imdb_id: false,
			year: false,
		})

		const errorMessages = ref({
			title: '',
			imdb_id: '',
			year: '',
		})

		// Search and create movie from OMDB (or similar service)
		const searchAndCreate = async () => {
			if (!searchTitle.value) return
			try {
				const url = `${apiUrl}/movies/create?title=${encodeURIComponent(
					searchTitle.value
				)}`
				const response = await fetch(url, {
					method: 'POST',
				})
				if (!response.ok) {
					throw new Error('Failed to create movie from search')
				}
				alert('Movie added successfully!')
				searchTitle.value = '' // Clean the search bar here
			} catch (error) {
				console.error(error)
				alert('Error creating movie')
			}
		}

		// Submit movie data directly
		const submitMovieForm = async () => {
			// Clear previous errors
			errorFields.value = {
				title: false,
				imdb_id: false,
				year: false,
			}
			errorMessages.value = {
				title: '',
				imdb_id: '',
				year: '',
			}

			try {
				const response = await fetch(`${apiUrl}/movies/create`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(movieForm.value),
				})

				if (!response.ok) {
					const errorData = await response.json()
					handleValidationErrors(errorData)
					throw new Error('Failed to add movie')
				}

				// If successful, reset the form and clear errors
				movieForm.value = {
					title: '',
					imdb_id: '',
					year: '',
					type: '',
					poster_url: '',
					genre: '',
					director: '',
					plot: '',
				}
				alert('Movie added successfully!')
			} catch (error) {
				console.error(error)
				alert('Error adding movie')
			}
		}

		// Handle validation errors and update error fields
		const handleValidationErrors = (errorData) => {
			errorData.detail.forEach((err) => {
				const field = err.loc[1]
				errorFields.value[field] = true
				errorMessages.value[field] = err.msg
			})
		}

		return {
			searchTitle,
			movieForm,
			errorFields,
			errorMessages,
			searchAndCreate,
			submitMovieForm,
		}
	},
}
</script>

<style scoped>
/* Style for error highlighting */
input.border-red-500,
textarea.border-red-500 {
	border-color: red;
}
</style>
