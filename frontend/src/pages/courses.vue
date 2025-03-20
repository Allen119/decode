<template>
  <div id="app" class="font-sans h-screen w-screen bg-white text-white flex flex-col"
    :style="{ fontFamily: 'Inter, sans-serif' }">
    <!-- Header -->
    <header class="bg-[rgba(217,217,217,1)] text-purple-700 p-4 flex justify-between items-center h-[7%] relative"
      :style="{ fontFamily: 'Inter, sans-serif' }">
      <!-- Logo and User ID Section -->
      <div class="flex items-center gap-4">
        <img src="@/assets/images/logo.png" alt="Logo" class="object-contain"
          :style="{ maxHeight: '80%', width: '10%', height: 'auto' }" />
        <span class="text-[150%] text-black">Your Courses</span>
      </div>
    </header>

    <div class="absolute bg-[#D9D9D9] w-[40%] h-[75%] top-[16%] left-[3.5%] rounded-[74px]">
      <div class="absolute bg-white w-[92%] h-[90%] top-[5%] left-[4%] rounded-[74px]">
        <h3 class="absolute text-lg text-black font-light left-[3%] top-[5%]">Created Courses</h3>
        <div class="absolute left-[3%] top-[12%] w-[90%] h-[80%] p-0 text-black font-light
        break-words overflow-y-auto">
          <div class="absolute left-[0%] top-[0%] w-full h-[100%] overflow-y-auto pr-4 ">
            <ul class="text-lg text-black font-light">
              <li v-for="(course, index) in courses" :key="course.name"
                class="p-2  border-gray-600 cursor-pointer hover:bg-gray-700 transition" @click="goToOwnerPage(course)">
                {{ index + 1 }}. {{ course.groupname }}
              </li>
            </ul>

          </div>
        </div>
      </div>
    </div>


    <div class="absolute bg-[#D9D9D9] w-[40%] h-[75%] top-[16%] right-[3.5%] rounded-[74px]">
      <div class="absolute bg-white w-[92%] h-[90%] top-[5%] right-[4%] rounded-[74px]">
        <h3 class="absolute text-lg text-black font-light left-[3%] top-[5%]">Joined Courses</h3>
        <div class="absolute left-[3%] top-[12%] w-[90%] h-[80%] p-0 text-black font-light
            break-words overflow-y-auto">
          <div class="absolute left-[0%] top-[0%] w-full h-[100%] overflow-y-auto pr-4">
            <ul class="text-lg text-black font-light">
              <li v-for="(course, index) in joinedCourses" :key="course.name"
                class="p-2  border-gray-600 cursor-pointer hover:bg-gray-700 transition"
                @click="goToMemberPage(course)">
                {{ index + 1 }}. {{ course.groupname }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router"; // Import Vue Router

// Reactive variables
const courses = ref([]);
const joinedCourses = ref([]);
const loading = ref(true);
const error = ref(null);
const router = useRouter();

// Fetch courses from Frappe API
const fetchCourses = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch("/api/method/decode.api.get_courses");

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Server Response:", data); // Debugging output

    courses.value = data.message || []; // Store the fetched course list
  } catch (err) {
    console.error("Error fetching courses:", err);
    error.value = "Failed to load courses.";
  } finally {
    loading.value = false;
  }
};

const goToOwnerPage = (course) => {
  if (course.name) {
    router.push({ name: "owner", params: { courseId: course.name } });
  }
};

// Fetch joined courses from Frappe API
const fetchJoinedCourses = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch("/api/method/decode.api.courses_joined"); // Replace with your actual API endpoint
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Server Response:", data); // Print response in console

    joinedCourses.value = data.message || []; // Ensure `message` is accessed correctly
  } catch (err) {
    console.error("Error fetching joined courses:", err);
    error.value = "Failed to load joined courses.";
  } finally {
    loading.value = false;
  }
};

const goToMemberPage = (course) => {
  if (course.name) {
    router.push({ name: "member", params: { courseId: course.name } });
  }
};

onMounted(() => {
  fetchCourses();
  fetchJoinedCourses();
});

</script>