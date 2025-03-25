<template>
  <div id="app" class="font-moulpali h-screen w-screen" :style="{
    background: 'linear-gradient(135deg, #000000, #262222)'
  }">
    <!-- Left Image -->
    <img src="@/assets/images/log.gif" alt="Left Image" class="absolute left-0 h-full" :style="{
      width: '45.63%',
      height: '100%'
    }" />
    <div class="absolute bg-white shadow-lg flex flex-col justify-center items-center" :style="{
      width: '41.67%',
      height: '80.62%',
      top: '7.24%',
      right: '6.0%',
      background: 'linear-gradient(135deg, #000000, #262222)'
    }">
      <!-- Centered Text at the Top -->
      <p class="text-center text-white text-[30px] mb-6 absolute" :style="{ top: '10%' }">
        CODE CAMPUS
      </p>

      <!-- Form Container -->
      <div class="p-6 space-y-6 w-full max-w-[600px] mt-16">
        <!-- Full Name Input -->
        <div>
          <label for="full-name" class="block text-white font-medium">Full Name</label>
          <input type="text" id="full-name" name="full-name" v-model="fullName"
            class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
            placeholder="Enter your full name" required />
        </div>
        <!-- Email Input -->
        <div>
          <label for="email" class="block text-white font-medium">Email</label>
          <input type="email" id="email" name="email" v-model="email"
            class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
            placeholder="Enter your email" required />
          <p v-if="emailError" class="text-red-500 text-sm mt-1">{{ emailError }}</p>
        </div>

        <!-- Password Input -->
        <div>
          <label for="password" class="block text-white font-medium">Password</label>
          <input type="password" id="password" name="password" v-model="password"
            class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
            placeholder="Enter your password" required />
          <p v-if="passwordError" class="text-red-500 text-sm mt-1">{{ passwordError }}</p>
        </div>

        <!-- Confirm Password Input -->
        <div>
          <label for="confirm-password" class="block text-white font-medium">Confirm Password</label>
          <input type="password" id="confirm-password" name="confirm-password" v-model="confirmPassword"
            class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
            placeholder="Confirm your password" required />
          <p v-if="confirmPasswordError" class="text-red-500 text-sm mt-1">{{ confirmPasswordError }}</p>
        </div>

        <!-- Register Button -->
        <div>
          <button @click="registerUser"
            class="w-[239px] h-[60px] bg-[#7DE5F4] text-white py-2 rounded hover:bg-[#227380] transition duration-200 transform"
            >
            Register
          </button>
          <p v-if="registerError" class="text-red-500 text-sm mt-1">{{ registerError }}</p>
        </div>

        <!-- "Do you already have an account?" text -->
        <div class="absolute right-[16%] top-[76%] text-gray-800 text-[16px]">
          Don't have an account?<br>Please use the
          <span @click="navigateTo('/signin')" class="text-[#7DE5F4] hover:text-[#5CC7E8] cursor-pointer">
            Sign in
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateTo = (path) => {
  router.push(path);
};

const fullName = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

const emailError = ref('');
const passwordError = ref('');
const confirmPasswordError = ref('');
const registerError = ref('');

const registerUser = async () => {
  // Reset previous errors
  emailError.value = '';
  passwordError.value = '';
  confirmPasswordError.value = '';
  registerError.value = '';

  // Validation checks
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    emailError.value = 'Please enter a valid email address.';
    return;
  }

  if (password.value.length < 6) {
    passwordError.value = 'Password must be at least 6 characters long.';
    return;
  }

  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = 'Passwords do not match.';
    return;
  }

  // Send registration data to API
  try {
    const response = await fetch('http://decode.local:8080/api/method/decode.api.register_user', {
      method: 'POST',
      credentials: 'include', // Include cookies
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        full_name: fullName.value,
        email: email.value,
        password: password.value
      })
    });

    const data = await response.json();

    console.log('Full response:', {
      status: response.status,
      body: data
    });

    if (response.ok) {
      if (data.message && data.message.message === "Registration successful!") {
        alert('Registration successful!');
        navigateTo('/signin');
      }else if(data.message.message === "Email already registered."){
      registerError .value = 'Email already registered';
      }
       else {
        registerError.value = 'Unexpected response from server';
      }
    } else {
      registerError.value = data.message?.message || 'Registration failed';
    }
  } catch (error) {
    console.error('Complete error:', error);
    registerError.value = 'Network error. Please try again.';
  }
};

</script>
<style scoped>
/* Add any custom styles here */
</style>
