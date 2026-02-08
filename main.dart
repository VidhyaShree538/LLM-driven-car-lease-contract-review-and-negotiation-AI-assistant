import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:convert';

void main() {
  runApp(const CarLeaseApp());
}

/* ---------------- APP ROOT ---------------- */

class CarLeaseApp extends StatelessWidget {
  const CarLeaseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Car Lease Contract',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.purple),
      home: const LoginPage(),
    );
  }
}

/* ---------------- LOGIN PAGE ---------------- */

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();

  void login() {
    if (_formKey.currentState!.validate()) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const UploadOptionsPage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Card(
          elevation: 10,
          margin: const EdgeInsets.all(24),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    "Car Lease Contract Login",
                    style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.deepPurple),
                  ),
                  const SizedBox(height: 20),
                  TextFormField(
                    decoration: const InputDecoration(
                      labelText: "Name",
                      prefixIcon: Icon(Icons.person),
                    ),
                    validator: (v) => v!.isEmpty ? "Enter name" : null,
                  ),
                  TextFormField(
                    decoration: const InputDecoration(
                      labelText: "Email",
                      prefixIcon: Icon(Icons.email),
                    ),
                    validator: (v) => v!.isEmpty ? "Enter email" : null,
                  ),
                  TextFormField(
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: "Password",
                      prefixIcon: Icon(Icons.lock),
                    ),
                    validator: (v) => v!.isEmpty ? "Enter password" : null,
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(onPressed: login, child: const Text("Login"))
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/* ---------------- LOGOUT DIALOG ---------------- */

void showLogoutDialog(BuildContext context) {
  showDialog(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text("Confirm Logout"),
      content: const Text("Are you sure you want to logout?"),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text("Cancel"),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(builder: (_) => const LoginPage()),
              (route) => false,
            );
          },
          child: const Text("Logout"),
        ),
      ],
    ),
  );
}

/* ---------------- UPLOAD OPTIONS PAGE ---------------- */

class UploadOptionsPage extends StatelessWidget {
  const UploadOptionsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Upload Options"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => showLogoutDialog(context),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton.icon(
              icon: const Icon(Icons.image),
              label: const Text("Upload Image"),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const UploadPage()),
                );
              },
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.picture_as_pdf),
              label: const Text("Upload PDF"),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const UploadPage()),
                );
              },
            ),
            const SizedBox(height: 20),
            // <-- NEW AI CHATBOT BUTTON -->
            ElevatedButton.icon(
              icon: const Icon(Icons.chat),
              label: const Text("AI Lease Assistant"),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const ChatbotPage()),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

/* ---------------- UPLOAD PAGE ---------------- */

class UploadPage extends StatefulWidget {
  const UploadPage({super.key});
  @override
  State<UploadPage> createState() => _UploadPageState();
}

class _UploadPageState extends State<UploadPage> {
  bool loading = false;
  String error = "";

  Future<void> uploadFile() async {
    setState(() {
      loading = true;
      error = "";
    });

    final picked = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
      withData: true,
    );

    if (picked == null) {
      setState(() => loading = false);
      return;
    }

    try {
      final file = picked.files.first;

      final request = http.MultipartRequest(
        'POST',
        Uri.parse("http://127.0.0.1:8000/extract-lease"),
      );

      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          file.bytes!,
          filename: file.name,
        ),
      );

      final response = await request.send();
      final body = await response.stream.bytesToString();
      final decoded = jsonDecode(body);

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OutputPage(
            contractData: decoded,
            redFlags: decoded['red_flags'] ?? [],
          ),
        ),
      );
    } catch (e) {
      error = "Upload failed: $e";
    }

    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Upload Lease"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => showLogoutDialog(context),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ElevatedButton.icon(
              onPressed: loading ? null : uploadFile,
              icon: const Icon(Icons.upload),
              label: const Text("Choose File"),
            ),
            const SizedBox(height: 20),
            if (loading) const CircularProgressIndicator(),
            if (error.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(12),
                child: Text(error,
                    style: const TextStyle(color: Colors.red)),
              ),
          ],
        ),
      ),
    );
  }
}

/* ---------------- OUTPUT PAGE ---------------- */

class OutputPage extends StatelessWidget {
  final Map<String, dynamic> contractData;
  final List redFlags;

  const OutputPage({
    super.key,
    required this.contractData,
    required this.redFlags,
  });

  String getFairnessStatus() {
    if (redFlags.isEmpty) return "Fair Contract ✅";
    if (redFlags.length <= 2) return "Needs Attention ⚠️";
    return "Potentially Unfair ❌";
  }

  @override
  Widget build(BuildContext context) {
    final lease = contractData['lease_agreement'] ?? {};
    final metrics = contractData['metrics'] ?? {};
    final carHistory = contractData['car_history'];

    return Scaffold(
      appBar: AppBar(
        title: const Text("Contract Analysis"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => showLogoutDialog(context),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _card("Agreement ID", lease['agreement_id']),
          _card("Lessor", lease['lessor']?['name']),
          _card("Lessee", lease['lessee']?['name']),
          _card("VIN", lease['vehicle_details']?['vin']),
          _card("Monthly Payment",
              lease['financial_terms']?['monthly_payment']),
          _card("Accuracy", metrics['accuracy']),
          const SizedBox(height: 20),

          ExpansionTile(
            title: const Text("Red Flags",
                style: TextStyle(color: Colors.red)),
            children: redFlags.isNotEmpty
                ? redFlags
                    .map((f) => ListTile(title: Text(f.toString())))
                    .toList()
                : [const ListTile(title: Text("No red flags detected"))],
          ),

          ExpansionTile(
            title: const Text("Fairness Assessment"),
            children: [
              ListTile(
                title: Text(
                  getFairnessStatus(),
                  style:
                      const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          if (carHistory != null)
            ElevatedButton.icon(
              icon: const Icon(Icons.history),
              label: const Text("View Car History"),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        CarHistoryPage(carHistory: carHistory),
                  ),
                );
              },
            ),
        ],
      ),
    );
  }

  Widget _card(String title, dynamic value) {
    return Card(
      child: ListTile(
        title: Text(title,
            style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(value?.toString() ?? "-"),
      ),
    );
  }
}

/* ---------------- CAR HISTORY PAGE ---------------- */

class CarHistoryPage extends StatelessWidget {
  final Map<String, dynamic> carHistory;

  const CarHistoryPage({super.key, required this.carHistory});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Car History"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => showLogoutDialog(context),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _historyCard("Ownership", carHistory['ownership']),
          _historyCard(
              "Accident History", carHistory['accident_history']),
          _historyCard("Usage Type", carHistory['usage_type']),
          _historyCard("Risk Level", carHistory['risk_level']),
        ],
      ),
    );
  }

  Widget _historyCard(String title, dynamic value) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.directions_car),
        title: Text(title,
            style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(value?.toString() ?? "Not available"),
      ),
    );
  }
}

/* ---------------- AI CHATBOT PAGE ---------------- */

class ChatbotPage extends StatefulWidget {
  const ChatbotPage({super.key});

  @override
  State<ChatbotPage> createState() => _ChatbotPageState();
}

class _ChatbotPageState extends State<ChatbotPage> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool loading = false;

  Future<void> _sendMessage(String message) async {
    if (message.isEmpty) return;

    setState(() {
      _messages.add({"role": "user", "text": message});
      loading = true;
    });
    _controller.clear();

    try {
      // Replace with your backend endpoint
      final response = await http.post(
        Uri.parse("http://127.0.0.1:8000/ask"), // your backend API
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"message": message}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _messages.add({"role": "ai", "text": data['reply']});
        });
      } else {
        setState(() {
          _messages.add({
            "role": "ai",
            "text": "Sorry, something went wrong. Try again."
          });
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({
          "role": "ai",
          "text": "Error connecting to server: $e"
        });
      });
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Car Lease Assistant")),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(8),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return Align(
                  alignment: msg['role'] == "user"
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: msg['role'] == "user"
                          ? Colors.purple[200]
                          : Colors.grey[300],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(msg['text']!),
                  ),
                );
              },
            ),
          ),
          if (loading)
            const Padding(
              padding: EdgeInsets.all(8),
              child: CircularProgressIndicator(),
            ),
          const Divider(height: 1),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                        hintText: "Ask about leases..."),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: () => _sendMessage(_controller.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
