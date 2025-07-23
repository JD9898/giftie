import { Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export const BACKEND_URL = 'https://c58df8c90b80.ngrok-free.app';

export default function ImportContactsScreen() {
  const handleImport = async () => {
    const fakeFriend = {
      name: 'Emily Wong',
      birthday: '2025-07-12',
      sentiment: 'Best friend',
      email: 'jademinwei.wang@gmail.com'
    };

    try {
      const res = await fetch(`${BACKEND_URL}/api/friends`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'Emily Wong',
          birthday: '2025-07-12',
          sentiment: 'Best friend',
          email: 'jademinwei.wang@gmail.com'
        }),
      });

      if (res.ok) {
        Alert.alert('Imported', `${fakeFriend.name} added successfully!`);
      } else {
        Alert.alert('Error', 'Failed to import contact.');
      }
    } catch (err) {
      Alert.alert('Network error', 'Could not connect to backend.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📲 Import Contacts</Text>
      <TouchableOpacity style={styles.button} onPress={handleImport}>
        <Text style={styles.buttonText}>Import Sample Contact</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    marginBottom: 24,
    fontWeight: 'bold',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});


