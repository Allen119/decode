<template>
  <div id="app">
    <!-- Left Sidebar -->
    <div
      class="absolute shadow-lg flex flex-col justify-start items-center w-[16.8%] h-screen top-0 left-0 bg-[#d96a6a]">

      <!-- Inner Box at Top of Sidebar -->
      <div
        class="w-full flex items-center px-4 h-[7%] bg-[#d9d9d9] border-[#2d2e4f]/35 transition-colors duration-300 ease-in-out flex-col justify-center">
        <img src="@/assets/images/Ellipse1.png" alt="Left Image"
          class="w-[30px] h-[30px] -translate-x-[80px] translate-y-[15px]" />
        <p class="text-[20px] font-light text-black translate-y-[-15px] truncate max-w-[200px]">
          {{ fullname }}
        </p>
      </div>

      <!-- Customizable Boxes -->
      <div
        class="absolute shadow-lg flex flex-col justify-start items-center overflow-y-auto w-full h-full top-[7%] left-0 bg-white scrollbar scrollbar-thumb-gray-400 scrollbar-track-gray-200">

        <!-- Boxes -->
        <div v-for="(box, index) in boxes" :key="box.id" :id="`box-${box.id}`" :data-index="index"
          class="w-full flex items-center px-4 cursor-pointer" :style="{
            height: box.height,
            width: box.width,
            backgroundColor: box.backgroundColor || 'rgba(217, 217, 217, 0.9)',
            transition: 'border-color 0.3s ease',
            marginTop: box.marginTop,
            justifyContent: 'center',
            borderRadius: box.borderRadius,
            border: box.border,
            position: box.position,
            fontSize: box.fontSize || '16px',
            transform: box.transform
          }" @click="handleBoxClick(box)">
          <!-- Logo Image on Left Side -->
          <img :src="box.logo" alt="Logo" :style="box.logoStyle" />

          <!-- Box Text -->
          <p class="font-light text-black mx-auto" :style="box.textStyle">
            {{ box.name }}
          </p>
        </div>

        <!-- Horizontal Line -->
        <div class="w-[100%] h-[2px] bg-gray-500 mt-10 mb-2"></div>

        <p class="text-xl font-bold mt-4 mb-4 transform translate-y-2 translate-x-[-71%]">
          Explore More
        </p>

        <!-- Explore Boxes -->
        <div v-for="(box, index) in explorebox" :key="box.id" :id="`box-${box.id}`" :data-index="index"
          class="w-full flex items-center px-4 cursor-pointer" :style="{
            height: box.height,
            width: box.width,
            backgroundColor: box.backgroundColor || 'rgba(217, 217, 217, 0.9)',
            transition: 'border-color 0.3s ease',
            marginTop: box.marginTop,
            justifyContent: 'center',
            borderRadius: box.borderRadius,
            position: box.position,
            fontSize: box.fontSize || '16px',
            transform: box.transform
          }" @click="handleBoxClick(box)">
          <!-- Logo Image on Left Side -->
          <img :src="box.logo" alt="Logo" :style="box.logoStyle" />

          <!-- Box Text -->
          <p class="font-light text-black mx-auto" :style="box.textStyle">
            {{ box.name }}
          </p>
        </div>
      </div>

    </div>



    <!-- Top Bar -->
    <div
      class="absolute shadow-lg flex flex-col justify-center items-center w-[82.58%] h-[7%] top-0 left-[17.42%] bg-[#d9d9d9]">

      <!-- Logo -->
      <img src="@/assets/images/logo.png" alt="Vertically Centered Image"
        class="object-contain max-h-[80%] absolute top-1/2 left-[80px] -translate-y-1/2" />


      <!-- Form Input Box -->
      <!-- <input type="text" placeholder="Search File & Courses"
  class="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#d9d9d9] text-[#d9d9d9] text-center w-[60%] h-[58%] leading-[2.5]" /> -->

      <p
        class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-black text-lg sm:text-4xl font-normal">
        Code. Collaborate. Create.
      </p>
    </div>

    <!-- Main Content Area -->
    <div
      class="absolute shadow-lg flex flex-col justify-center items-center transition-all duration-100 w-[82.58%] h-screen top-[7%] left-[17.42%] bg-[#d9d9d9]"
      :class="{ 'blur-sm': showContainer || showCreateContainer }">
      <!-- 'Create' Text (Click to Show Blank Container) -->
      <p class="text-[64px] font-medium text-[rgba(45,46,79,0.35)] font-inter max-w-[80%] max-h-[80%] cursor-pointer hover:opacity-80 mt-4"
        @click="toggleCreateContainer">
        Create
      </p>
      <!-- '||' Text -->
      <p class="text-[24px] font-medium text-[rgba(45,46,79,0.35)] font-inter">
        ||
      </p>

      <!-- Image -->
      <img src="@/assets/images/createjoin.svg" alt="Centered Image"
        class="object-contain cursor-pointer hover:opacity-80 max-w-[80%] max-h-[80%] mt-4"
        @click="toggleJoinContainer" />

      <!-- <p class="text-[20px] font-bold mt-4 mb-4 transform translate-y-[100px] translate-x-[-579%]">
    Recent files
  </p> -->

      <div v-if="visibleContainers[7]"
        class="new-container absolute top-20 left-15 w-[450px] h-[80px] bg-[rgba(217,217,217,1)] rounded-md shadow-lg flex items-center justify-center z-50 transform translate-y-[300%]">
        <div class="flex items-center justify-center w-full space-x-4">
          <!-- Input Box -->
          <input type="text" v-model="lastFileUuid" placeholder="Enter UUID"
            class="w-[300px] h-[40px] p-2 rounded-md border-2 border-gray-300" />

          <!-- Save Button -->
          <button class="w-[100px] h-[40px] bg-[rgba(40,41,71,1)] text-white rounded-md hover:bg-[#797a9c]"
            @click="enterfile">
            Enter
          </button>
          <p v-if="errorMessage" class="text-red-500">{{ errorMessage }}</p>
        </div>
      </div>

      <!-- New Container for box.id === 9 -->
      <div v-if="visibleContainers[9]"
        class="new-container absolute top-[10%] left-15 w-[25%] h-auto max-h-[45%] bg-white rounded-[25px] p-4 overflow-y-auto">
        <h2 class="text-black text-lg font-semibold mb-2">Your Files</h2>

        <ul v-if="codingFiles.length > 0">
          <li v-for="file in codingFiles" :key="file.name"
            class="text-black p-2 cursor-pointer hover:bg-gray-800 rounded-md" @click="navigateToFile(file.name)">
            {{ file.filename }}
          </li>
        </ul>

        <p v-else class="text-gray-400">No files found.</p>
      </div>

      <!-- Boxes
      <div v-for="(box, index) in recentbox" :key="box.id" :id="`box-${box.id}`" :data-index="index"
        class="w-full flex items-center px-4 cursor-pointer" :style="{
          top: '5%',
          height: box.height,
          width: box.width,
          backgroundColor: box.backgroundColor || 'rgba(217, 217, 217, 0.9)',
          transition: 'border-color 0.3s ease',
          marginTop: box.marginTop,
          justifyContent: 'center',
          borderRadius: box.borderRadius,
          border: box.border,
          position: box.position,
          fontSize: box.fontSize || '20px',
          transform: box.transform
        }" @click="handleBoxClick(box)">
        <p class="font-light text-black mx-auto" :style="box.textStyle">
          {{ box.name }}
        </p>
      </div> -->
      <button @click="handleLogout"
        class="absolute top-[85%] right-12 bg-[rgba(40,41,71,1)] text-white font-bold rounded-[7px] hover:opacity-90 focus:outline-none w-36 h-12 flex items-center justify-center transform translate-y-[10px]">
        <div class="flex items-center space-x-2">
          <span>Logout</span>
        </div>
      </button>


    </div>

    <!-- Button to toggle container (Outside main content area) -->
    <button @click="toggleContainer"
      class="absolute right-12 bg-[rgba(40,41,71,1)] text-white font-bold rounded-[7px] hover:opacity-90 focus:outline-none w-36 h-12 flex items-center justify-center transform translate-y-[10px]">
      <div class="flex items-center space-x-2">
        <img src="@/assets/images/plus.svg" alt="Icon" class="w-6 h-6 rounded-full object-contain" />
        <span>Create File</span>
      </div>
    </button>


    <!-- New Container (Outside main content area) -->
    <div v-if="showContainer" ref="containerRef"
      class="absolute top-20 right-12 w-[450px] h-[80px] bg-[rgba(217,217,217,1)] rounded-md shadow-lg flex items-center justify-center z-50 transform translate-y-2">
      <div class="flex items-center justify-center w-full space-x-4">
        <!-- Input Box -->
        <input type="text" v-model="fileName" placeholder="Enter file name"
          class="w-[300px] h-[40px] p-2 rounded-md border-2 border-gray-300" />

        <!-- Save Button -->
        <button @click="saveFile"
          class="w-[100px] h-[40px] bg-[rgba(40,41,71,1)] text-white rounded-md hover:bg-[#797a9c]">
          Save
        </button>
      </div>
    </div>

    <div v-if="showCreateContainer" ref="createContainerRef"
      class="fixed inset-0 flex items-center justify-center bg-white w-[30%] h-[40%] top-[30%] left-[40%]">
      <div class="bg-white p-6 rounded-lg shadow-lg w-[100%] h-[100%]">
        <h2 class="text-xl font-bold mb-4">Create New Course</h2>
        <!-- Project Name Input -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Course Name</label>
          <input type="text" v-model="projectName" placeholder="Enter course name"
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#d9d9d9]" />
          <p v-if="courseNameError" class="text-red-500 text-sm mt-1">{{ courseNameError }}</p>
        </div>
        <!-- Username Input (Uneditable) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Username</label>
          <input type="text" :value="fullname" disabled
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed" />
        </div>
        <!-- Project Description Input -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Course Description</label>
          <textarea v-model="projectDescription" placeholder="Enter course description"
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#d9d9d9]"></textarea>
        </div>
        <!-- Create Button -->
        <div class="flex justify-end">
          <button @click="validateAndCreate"
            class="bg-[rgba(40,41,71,1)] text-white font-bold rounded-md px-4 py-2 hover:bg-[#797a9c] focus:outline-none">
            Create
          </button>
        </div>
      </div>
    </div>

    <div v-if="showJoinContainer" ref="joinContainerRef"
      class="fixed inset-0 flex items-center justify-center bg-white w-[30%] h-[30%] top-[30%] left-[40%]">
      <div class="bg-white p-6 rounded-lg shadow-lg w-[100%] h-[100%]">
        <h2 class="text-xl font-bold mb-4">Join New Course</h2>
        <!-- Project Name Input -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Course Id</label>
          <input type="text" v-model="courseId" placeholder="Enter course id"
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#d9d9d9]" />
          <p v-if="courseIdError" class="text-red-500 text-sm mt-1">{{ courseIdError }}</p>
        </div>
        <!-- Username Input (Uneditable) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Username</label>
          <input type="text" :value="fullname" disabled
            class="mt-1 block w-full p-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed" />
        </div>
        <!-- Create Button -->
        <div class="flex justify-end">
          <button @click="validateAndJoin"
            class="bg-[rgba(40,41,71,1)] text-white font-bold rounded-md px-4 py-2 hover:bg-[#797a9c] focus:outline-none">
            Join
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import plusLogo from '@/assets/images/plus.svg';
import Homelog from '@/assets/images/Homelog.svg';
import files from '@/assets/images/filess.svg';
import project from '@/assets/images/projects.svg';
import course from '@/assets/images/course.svg';
import profile from '@/assets/images/profile.svg';
import documentation from '@/assets/images/documentation.svg';
import settings from '@/assets/images/Settings.svg';
import help from '@/assets/images/Help.svg';

import { useRouter } from "vue-router";

const router = useRouter(); // Initialize the router instance

const navigateTo = (path) => {
  router.push(path); // Use the router instance to navigate
};
const fullname = ref('')

// Dynamically managed boxes with custom styles
const boxes = ref([
  // {
  //   id: 1,
  //   name: 'Create project',
  //   logo: plusLogo,
  //   height: '5%',
  //   width: '94%',
  //   backgroundColor: 'rgba(255, 255, 255, 1)',
  //   border: '1px solid rgba(45, 46, 79, 0.35)',
  //   borderRadius: '7px',
  //   position: 'relative',
  //   marginTop: '20px',
  //   fontSize: '20px',
  //   logoStyle: { width: '22px', height: '22px', marginRight: '15px', transform: 'translateY(0px) translateX(40px)' },
  //   textStyle: { transform: 'translateX(-20px)' }
  // },
  {
    id: 3,
    name: 'Home',
    logo: Homelog,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    //border: '1px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '10%', transform: 'translateX(-6.5px) translateY(-1.5px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(-6px)' }
  },
  {
    id: 9,
    name: 'Files',
    logo: files,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(-8px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(-17.5px)' }
  },
  // {
  //   id: 5,
  //   name: 'Projects',
  //   logo: project,
  //   height: '4%',
  //   width: '37%',
  //   backgroundColor: 'rgba(255, 255, 255, 1)',
  //   borderRadius: '7px',
  //   position: 'relative',
  //   marginTop: '24px',
  //   fontSize: '20px',
  //   logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(5px) translateY(0px)' },
  //   transform: 'translateX(-93px)',
  //   textStyle: { transform: 'translateX(0px)' }
  // },
  {
    id: 6,
    name: 'Courses',
    logo: course,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(5px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(0px)' }
  },
  {
    id: 7,
    name: 'UUID',
    logo: profile,
    height: '4%',
    width: '37%',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    borderRadius: '7px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(-3px) translateY(0px)' },
    transform: 'translateX(-93px)',
    textStyle: { transform: 'translateX(-7.5px)' }
  },
]);

const explorebox = ref([
  // {
  //   id: 1,
  //   name: 'Documentation',
  //   logo: documentation,
  //   height: '4%',
  //   width: '60%',
  //   backgroundColor: 'rgba(255, 255, 255, 1)',
  //   borderRadius: '7px',
  //   position: 'relative',
  //   marginTop: '24px',
  //   fontSize: '20px',
  //   logoStyle: { width: '30px', height: '30px', marginRight: '10px', transform: 'translateX(-2px) translateY(0px)' },
  //   transform: 'translateX(-55.0px)',
  //   textStyle: { transform: 'translateX(-3px)' }
  // },
  // {
  //   id: 4,
  //   name: 'Settings',
  //   logo: settings,
  //   height: '4%',
  //   width: '37%',
  //   backgroundColor: 'rgba(255, 255, 255, 1)',
  //   borderRadius: '7px',
  //   position: 'relative',
  //   marginTop: '24px',
  //   fontSize: '20px',
  //   logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
  //   transform: 'translateX(-93px)',
  //   textStyle: { transform: 'translateX(1px)' }
  // },
  // {
  //   id: 5,
  //   name: 'Help',
  //   logo: help,
  //   height: '4%',
  //   width: '37%',
  //   backgroundColor: 'rgba(255, 255, 255, 1)',
  //   borderRadius: '7px',
  //   position: 'relative',
  //   marginTop: '24px',
  //   fontSize: '20px',
  //   transform: 'translateX(-93px)',
  //   logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(-5.5px) translateY(0px)' },
  //   textStyle: { transform: 'translateX(-15px)' }
  // },
]);

const recentbox = ref([
  {
    id: 1,
    name: 'File 1',
    //logo: documentation,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '10px', transform: 'translateX(-2px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },
  {
    id: 2,
    name: 'File 2',
    //logo: settings,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },

  {
    id: 3,
    name: 'Course 1',
    //logo: settings,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },

  {
    id: 4,
    name: 'Course 2',
    //logo: settings,
    height: '5%',
    width: '85%',
    backgroundColor: 'rgba(217, 217, 217, 1)',
    border: '0.5px solid rgba(45, 46, 79, 0.35)',
    borderRadius: '14px',
    position: 'relative',
    marginTop: '24px',
    fontSize: '20px',
    logoStyle: { width: '30px', height: '30px', marginRight: '15px', transform: 'translateX(7.5px) translateY(0px)' },
    transform: 'translateX(-55px) translateY(30px)',
    textStyle: { transform: 'translateX(-570px)' }
  },
]);


const fetchUserFullname = async () => {
  try {
    const response = await fetch('/api/method/decode.api.get_user_fullname', {
      method: 'GET',
      credentials: 'include', // Ensures session-based authentication
    })

    // Handle non-200 responses
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()

    if (data.message?.fullname) {
      fullname.value = data.message.fullname
    } else {
      fullname.value = '...'
    }
  } catch (err) {
    console.error('Error fetching fullname:', err)
    fullname.value = 'Error loading data'
  }
}

const performAction = () => {
  console.log('Clicked');
  // Add your custom logic here, e.g., navigating to a new route or triggering a modal
  //alert('Action performed!');
};

const fileName = ref(""); // Holds the input file name
const saveError = ref(""); // Holds error messages

const projectName = ref('');
const projectDescription = ref('');
const courseId = ref('');
const courseNameError = ref("");
const courseIdError = ref("");

// References for containers
const containerRef = ref(null)
const createContainerRef = ref(null)
const joinContainerRef = ref(null)

// States to track visibility
const showContainer = ref(false)
const showCreateContainer = ref(false)
const showJoinContainer = ref(false)



// Toggle functions for each container
const toggleContainer = () => {
  showContainer.value = !showContainer.value
}

const toggleCreateContainer = () => {
  showCreateContainer.value = !showCreateContainer.value
}

const toggleJoinContainer = () => {
  showJoinContainer.value = !showJoinContainer.value
}

// Handle clicks outside of containers
const handleClickOutside = (event) => {
  if (
    (showCreateContainer.value &&
      createContainerRef.value &&
      !createContainerRef.value.contains(event.target) &&
      !event.target.closest('p')) ||
    (showContainer.value &&
      containerRef.value &&
      !containerRef.value.contains(event.target) &&
      !event.target.closest('button')) ||
    (showJoinContainer.value &&
      joinContainerRef.value &&
      !joinContainerRef.value.contains(event.target) &&
      !event.target.closest('img')) // Assuming the join container opens via an image click
  ) {
    showCreateContainer.value = false
    showContainer.value = false
    showJoinContainer.value = false
  }
}

const validateAndCreate = () => {
  if (!projectName.value.trim()) {
    courseNameError.value = "Course name cannot be empty.";
    return;
  }
  courseNameError.value = ""; // Clear error if valid

  createProject();
};


const createProject = async () => {
  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.reg_group", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        groupname: projectName.value,
        description: projectDescription.value,
      }),
    });

    console.log("Raw Response:", response); // Log raw response

    const data = await response.json();

    console.log("API Response:", data); // Log parsed API response

    if (data.message && data.message.name && data.message.message == "Group registered successfully!") {
      //alert(data.message.message); //Show success message
      courseId.value = data.message.name;
      window.location.href = `http://decode.local:8080/frontend/owner/${courseId.value}`; // Redirect
    }
    else if (data.message.message == "Group name already exists.") {
      courseNameError.value = "Course name already exists. Please enter a different name.";
    }
    else {
      alert("Something unexpected happened. Please try again.");
    }
  } catch (error) {
    console.error("Fetch Error:", error); // Log error details
    alert("Error creating group: " + error.message);
  }
};


const validateAndJoin = () => {
  if (!courseId.value.trim()) {
    courseIdError.value = "Course ID cannot be empty.";
    return;
  }
  courseIdError.value = ""; // Clear error if valid

  joinProject();
};

const joinProject = async () => {
  try {
    const response = await fetch(`http://decode.local:8080/api/method/decode.api.join_project?course_id=${encodeURIComponent(courseId.value)}`, {
      method: "GET",
      credentials: "include",
    });

    const data = await response.json();
    console.log("Server Response:", data);

    if (data.message.message == "Course found.") {
      window.location.href = `http://decode.local:8080/frontend/member/${courseId.value}`; // Redirect
    }
    else if (data.message.message == "User already a member of the group.") {
      courseIdError.value = "User already a member of the group.";
    }
    else {
      courseIdError.value = "Enter a valid Course ID"; // Show error message
    }

  } catch (error) {
    console.error("Error joining project:", error);
    courseIdError.value = "Network error. Please try again."; // Handle network errors
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchUserFullname()
  onMounted(fetchCodingFiles);
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const saveFile = async () => {
  if (!fileName.value.trim()) {
    saveError.value = "Please enter a file name.";
    return;
  }

  // Determine the language based on the file extension
  const language = fileName.value.endsWith(".py") ? "Python" : "Unknown";

  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.codingFiles", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file_name: fileName.value,
        language: language,
        code: "", // Include code content if needed
      }),
    });

    const data = await response.json();
    console.log("Full API Response:", data);

    if (data.message) {
      alert(data.message.message); // Show success message
      console.log("User Document:", data.message.user);
      const lastFileUuid = data.message.user.codingfiles[data.message.user.codingfiles.length - 1].name;

      // Navigate to filecode with the UUID
      router.push(`/filecode/${lastFileUuid}`);
    } else {
      saveError.value = "An unexpected error occurred.";
    }
  } catch (error) {
    console.error("Save file error:", error);
    saveError.value = "Failed to save the file. Please try again.";
  }

  // Clear the file name input
  fileName.value = "";
};
const visibleContainers = ref({})

const handleBoxClick = (box) => {
  if (box.id === 7) {
    // Toggle container visibility
    visibleContainers.value[box.id] = !visibleContainers.value[box.id]
  }
  else if (box.id === 6) {
    router.push({ name: "courses" }); // Redirects to /courses
  }
  else if (box.id === 9) {
    visibleContainers.value[box.id] = !visibleContainers.value[box.id];
    if (visibleContainers.value[box.id]) {
      fetchCodingFiles(); // Fetch data when the container opens
    }
  }
};

const codingFiles = ref([]); // ✅ Ensure codingFiles is initialized

const fetchCodingFiles = async () => {
  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.get_coding_files");
    const responseData = await response.json();
    console.log("Response received:", responseData);

    // Access the actual data structure through message property
    if (responseData.message && responseData.message.status === "success") {
      codingFiles.value = responseData.message.data; // Access data through message
      console.log("codingFiles after update:", codingFiles.value);
    } else {
      console.error("Error fetching files:", responseData.message ? responseData.message.message : "Unknown error");
    }
  } catch (error) {
    console.error("API Error:", error);
  }
};

const navigateToFile = (filename) => {
  if (filename) {
    router.push({ name: "filecode", params: { uuid: filename } });
  }
};

const lastFileUuid = ref(""); // Store UUID from input
const errorMessage = ref(""); // Store error message


const enterfile = async () => {
  errorMessage.value = ""; // Reset error message

  if (!lastFileUuid.value.trim()) {
    errorMessage.value = "Please enter a valid UUID";
    return;
  }

  console.log("Sending UUID:", lastFileUuid.value); // ✅ Debugging

  try {
    const response = await fetch(
      `http://decode.local:8080/api/method/decode.api.findbyuuid?uuid=${encodeURIComponent(lastFileUuid.value)}`
    );

    console.log("Response status:", response.status); // ✅ Debugging

    if (!response.ok) {
      throw new Error("Server error. Please try again later.");
    }

    const result = await response.json();
    console.log("API Response:", result); // ✅ Debugging

    if (result.message) {
      router.push(`/filecode/${result.message}`);
    } else {
      errorMessage.value = "Invalid UUID. Please enter a valid one.";
    }
  } catch (error) {
    console.error("Fetch Error:", error);
    errorMessage.value = "Network error. Check your connection.";
  }
};

const handleLogout = async () => {
  try {
    // Call backend to set x = None
    const response = await fetch("http://decode.local:8080/api/method/decode.api.logout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Parse JSON response
    const data = await response.json();
    console.log("Server Response:", data); // ✅ Print server response

    // Redirect to /signin
    router.push("/signin");
  } catch (error) {
    console.error("Logout failed:", error);
  }
};

</script>

<style scoped>
/* Apply Inter font to the entire component */
body {
  font-family: 'Inter', sans-serif;
}

/* Optional: Keep the .font-inter class if needed for specific overrides */
.font-inter {
  font-family: 'Inter', sans-serif;
}
</style>