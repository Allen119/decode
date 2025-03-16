<template>
  <div id="app" class="font-moulpali h-screen w-screen" :style="{
    background: 'linear-gradient(135deg, #000000, #262222)'
  }">
    <!-- Left Image -->
    <img src="@/assets/images/log.gif" alt="Left Image" class="absolute left-0 h-full" :style="{
      width: '45.63%',
      height: '100%'
    }" />
    <div class="absolute bg-white shadow-lg" :style="{
      width: '41.67%',
      height: '61.62%',
      top: '19.24%',
      right: '6.0%',
      background: 'linear-gradient(135deg, #000000, #262222)'
    }">
      <!-- Centered Text at the Top -->
      <p class="absolute text-center text-white text-[30px] top-[16%] w-full">
        CODE CAMPUS
      </p>

      <!-- Content inside the container -->
      <div class="flex justify-center items-center h-full">
        <form @submit.prevent="loginUser" class="p-6 space-y-4 w-full max-w-[600px]">
          <!-- Email Input -->
          <div>
            <label for="email" class="block text-white font-medium">Email</label>
            <input v-model="email" type="email" id="email" name="email"
              class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
              placeholder="Enter your email" required />
          </div>

          <!-- Password Input -->
          <div>
            <label for="password" class="block text-white font-medium">Password</label>
            <input v-model="password" type="password" id="password" name="password"
              class="w-full h-[70px] bg-gray-800 text-gray-700 px-4 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:text-white placeholder:text-gray-500"
              placeholder="Enter your password" required />
          </div>

          <!-- Login Button -->
          <div>
            <button type="submit"
              class="w-[239px] h-[60px] bg-[#7DE5F4] text-white py-2 rounded hover:bg-[#227380] transition duration-200 transform translate-x-[0%] translate-y-[12%]">
              Login
            </button>
          </div>

          <!-- Error Message -->
          <div v-if="loginError" class="text-red-500 text-center mt-4 translate-x-[-28%]">
            {{ loginError }}
          </div>

          <!-- "Don't have an account?" text placed on the right side of the button -->
          <div class="absolute right-[16%] top-[61%] text-gray-800 text-[16px]">
            Don't have an account?<br>Please use the
            <span @click="navigateTo('/register')" class="text-[#7DE5F4] hover:text-[#5CC7E8] cursor-pointer">
              Register
            </span>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const loginError = ref('');
const router = useRouter();

const navigateTo = (path) => {
  router.push(path);
};

const loginUser = async () => {
  loginError.value = "";
  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.login_user", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    });
    
    const data = await response.json();
    console.log('Full API Response:', data);
    
    // Check for deeply nested structure
    if (data.message && data.message.message && data.message.message.message === "Login successful!") {
      localStorage.setItem("userToken", data.message.message.token); // Store the token
      console.log('Token:', data.message.message.token);
      localStorage.setItem("isAuthenticated", "true"); // Store login status
      router.push("/main"); // Redirect to the main page
    } else {
      loginError.value = "Invalid credentials. Please try again.";
    }
  } catch (error) {
    console.error("Login error:", error);
    loginError.value = "Network error. Please try again.";
  }
};

</script>



<!-- In [5]: all_users = frappe.get_all("user_reg", fields=["*"])  # Fetch all user data
   ...: 
   ...: user_data = []
   ...: 
   ...: for user in all_users:
   ...:     user_doc = frappe.get_doc("user_reg", user.name)  # Fetch full document
   ...:     user_entry = user.copy()  # Copy all user details
   ...:     user_entry["codingfiles"] = []  # Add child table field
   ...: 
   ...:     for child in user_doc.codingfiles:  # Loop through child table
   ...:         user_entry["codingfiles"].append(child.as_dict())  # Append child data
   ...: 
   ...:     user_data.append(user_entry)  # Store structured data
   ...: 
   ...: # Print the full structured data
   ...: import pprint
   ...: pprint.pprint(user_data)
   ...: 
[{'_assign': None,
  '_comments': None,
  '_liked_by': None,
  '_user_tags': None,
  'codingfiles': [{'code': 'dfdfdfdffdsfdvd',
                   'creation': datetime.datetime(2025, 2, 6, 22, 23, 15, 258545),
                   'docstatus': 0,
                   'doctype': 'codingFiles',
                   'filename': 'df',
                   'idx': 1,
                   'language': 'ss',
                   'modified': datetime.datetime(2025, 2, 13, 14, 9, 8, 664871),
                   'modified_by': 'Administrator',
                   'name': '0194dc3a-05bc-7471-9091-a44c7202d242',
                   'owner': 'Administrator',
                   'parent': '0194dc2e-157e-77d3-ac18-0063e13e3d8c',
                   'parentfield': 'codingfiles',
                   'parenttype': 'user_reg'},
                  {'code': '',
                   'creation': datetime.datetime(2025, 2, 6, 22, 23, 15, 258545),
                   'docstatus': 0,
                   'doctype': 'codingFiles',
                   'filename': 'dd.py',
                   'idx': 2,
                   'language': 'Python',
                   'modified': datetime.datetime(2025, 2, 13, 14, 9, 8, 664871),
                   'modified_by': 'Administrator',
                   'name': '0194e1d2-2590-7a61-b3f6-c3972d52bc8d',
                   'owner': 'Administrator',
                   'parent': '0194dc2e-157e-77d3-ac18-0063e13e3d8c',
                   'parentfield': 'codingfiles',
                   'parenttype': 'user_reg'},
                  {'code': '',
                   'creation': datetime.datetime(2025, 2, 6, 22, 23, 15, 258545),
                   'docstatus': 0,
                   'doctype': 'codingFiles',
                   'filename': 'dsfkodofdj.py',
                   'idx': 3,
                   'language': 'Python',
                   'modified': datetime.datetime(2025, 2, 13, 14, 9, 8, 664871),
                   'modified_by': 'Administrator',
                   'name': '0194fe76-3a7d-7710-8653-5bed717623b4',
                   'owner': 'Administrator',
                   'parent': '0194dc2e-157e-77d3-ac18-0063e13e3d8c',
                   'parentfield': 'codingfiles',
                   'parenttype': 'user_reg'}],
  'creation': datetime.datetime(2025, 2, 6, 22, 23, 15, 258545),
  'docstatus': 0,
  'email': 'ff@gmail.com',
  'fullname': 'Navaneeth',
  'idx': 0,
  'modified': datetime.datetime(2025, 2, 13, 14, 9, 8, 664871),
  'modified_by': 'Administrator',
  'name': '0194dc2e-157e-77d3-ac18-0063e13e3d8c',
  'owner': 'Administrator',
  'password': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'},
 {'_assign': None,
  '_comments': None,
  '_liked_by': None,
  '_user_tags': None,
  'codingfiles': [{'code': 'fsjsdksdpkd',
                   'creation': datetime.datetime(2025, 1, 28, 22, 16, 57, 461911),
                   'docstatus': 0,
                   'doctype': 'codingFiles',
                   'filename': 'ee.py',
                   'idx': 1,
                   'language': 'Python',
                   'modified': datetime.datetime(2025, 2, 13, 13, 58, 52, 747814),
                   'modified_by': 'Administrator',
                   'name': '0194aded-d371-76b0-a17f-d6e2edb91abe',
                   'owner': 'Administrator',
                   'parent': '0194adcf-15b7-7d81-a641-fc497681d666',
                   'parentfield': 'codingfiles',
                   'parenttype': 'user_reg'},
                  {'code': 'hi hi hihi',
                   'creation': datetime.datetime(2025, 1, 28, 22, 16, 57, 461911),
                   'docstatus': 0,
                   'doctype': 'codingFiles',
                   'filename': 'f3.py',
                   'idx': 2,
                   'language': 'python',
                   'modified': datetime.datetime(2025, 2, 13, 13, 58, 52, 747814),
                   'modified_by': 'Administrator',
                   'name': '0194adee-cc59-7343-9744-7d5d54218cc9',
                   'owner': 'Guest',
                   'parent': '0194adcf-15b7-7d81-a641-fc497681d666',
                   'parentfield': 'codingfiles',
                   'parenttype': 'user_reg'},
                  {'code': '',
                   'creation': datetime.datetime(2025, 1, 28, 22, 16, 57, 461911),
                   'docstatus': 0,
                   'doctype': 'codingFiles',
                   'filename': 'fnkf.py',
                   'idx': 3,
                   'language': 'Python',
                   'modified': datetime.datetime(2025, 2, 13, 13, 58, 52, 747814),
                   'modified_by': 'Administrator',
                   'name': '0194adff-364c-73c1-8146-3aecfbd86570',
                   'owner': 'Administrator',
                   'parent': '0194adcf-15b7-7d81-a641-fc497681d666',
                   'parentfield': 'codingfiles',
                   'parenttype': 'user_reg'},
                  {'code': '',
                   'creation': datetime.datetime(2025, 1, 28, 22, 16, 57, 461911),
                   'docstatus': 0,
                   'doctype': 'codingFiles',
                   'filename': 're.py',
                   'idx': 4,
                   'language': 'Python',
                   'modified': datetime.datetime(2025, 2, 13, 13, 58, 52, 747814),
                   'modified_by': 'Administrator',
                   'name': '0194ae00-ad50-7f81-b766-b78c081262c6',
                   'owner': 'Administrator',
                   'parent': '0194adcf-15b7-7d81-a641-fc497681d666',
                   'parentfield': 'codingfiles',
                   'parenttype': 'user_reg'}],
  'creation': datetime.datetime(2025, 1, 28, 22, 16, 57, 461911),
  'docstatus': 0,
  'email': 'gg@gmail.com',
  'fullname': 'Allen',
  'idx': 0,
  'modified': datetime.datetime(2025, 2, 13, 13, 58, 52, 747814),
  'modified_by': 'Administrator',
  'name': '0194adcf-15b7-7d81-a641-fc497681d666',
  'owner': 'Administrator',
  'password': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'}]
 -->
