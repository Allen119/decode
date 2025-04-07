<template>
  <div id="app" class="font-moulpali h-screen w-screen" :style="{
    //background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.9))', 
    background: 'linear-gradient(135deg, #000000, #262222)'
  }">
    <header class="flex justify-between items-center p-5 flex-wrap">
      <!-- Logo on the left with size adjustment -->
      <div class="flex items-center mb-4 sm:mb-0">
  <img src="@/assets/images/logo.png" alt="CodeCampus Logo"
    class="mr-3" style="width: 13%; height: auto;" />
  <div class="text-2xl font-bold text-white">Code Campus</div>
</div>


      <!-- Buttons on the right -->
      <div class="flex gap-4">
        <button class="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600" @click="navigateTo('/signin')">Sign
          In</button>
        <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-400"
          @click="navigateTo('/register')">Register</button>
      </div>
    </header>

    <main class="mt-10 text-center">
      <h1 class="text-4xl font-bold mb-4 text-white text-lg sm:text-4xl">Code. Collaborate. Create.</h1>
      <p class="text-gray-400 mb-8 text-sm sm:text-base">A powerful online IDE that lets you code from anywhere. Start
        coding in seconds.</p>
      <div class="flex justify-center gap-6 mb-10 flex-wrap">
        <button class="px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-400" @click="openDialog">
          Get Started
        </button>
        <button class="px-6 py-3 bg-gray-700 text-white rounded hover:bg-gray-600" @click="learnMore">Learn
          More</button>
      </div>

      <!-- Features Section -->
      <div class="flex justify-center gap-6 mb-10 animate-slide-in flex-wrap">
        <div class="bg-gray-800 p-6 rounded shadow-md feature-card w-full sm:w-1/2 md:w-1/3" v-for="feature in features"
          :key="feature.title">
          <h3 class="text-xl font-semibold text-blue-400 mb-2">{{ feature.title }}</h3>
          <p class="text-gray-400">{{ feature.description }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Dialog } from 'frappe-ui';
import { useRouter } from 'vue-router';

const router = useRouter();
const features = ref([
  { title: 'Code Anywhere', description: 'Access your development environment from any browser. No setup required.' },
  { title: 'Real-time Collaboration', description: 'Work together with your team in real-time. Share your workspace instantly.' },
  { title: 'Multiple Languages', description: 'Support for all major programming languages and frameworks.' }
]);

const openDialog = () => {
  const dialog = new Dialog({
    title: 'Welcome to CodeSpace!',
    body: 'Start coding in seconds with our powerful online IDE.',
    primary_action: {
      label: 'Get Started',
      action() {
        dialog.hide();
        alert('Getting started...');
      }
    }
  });
  dialog.show();
};
const navigateTo = (path) => {
  router.push(path);
};
const signIn = () => alert('Sign In clicked');
const register = () => alert('Register clicked');
const learnMore = () => alert('Learn more about CodeSpace...');
</script>

<style scoped>
/* Add any additional custom styles here if needed */
#app {
  min-height: 100vh;
  background-size: cover;
  background-position: center;
}

/* Flex container for features */
.feature-card {
  opacity: 0;
  transform: translateX(-100%);
  transition: all 0.5s ease-in-out;
}

/* Animation for sliding in */
@keyframes slideIn {
  0% {
    opacity: 0;
    transform: translateX(-100%);
  }

  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Apply animation to the features section */
.animate-slide-in .feature-card {
  animation: slideIn 1s forwards;
}

/* Delay the animation for each feature card */
.animate-slide-in .feature-card:nth-child(1) {
  animation-delay: 0.2s;
}

.animate-slide-in .feature-card:nth-child(2) {
  animation-delay: 0.4s;
}

.animate-slide-in .feature-card:nth-child(3) {
  animation-delay: 0.6s;
}

/* Responsive Styles */
@media (max-width: 640px) {
  .feature-card {
    width: 100%;
  }

  h1 {
    font-size: 2rem;
  }

  p {
    font-size: 1rem;
  }
}

@media (min-width: 640px) {
  .feature-card {
    width: 48%;
  }
}

@media (min-width: 768px) {
  .feature-card {
    width: 30%;
  }
}
</style>
