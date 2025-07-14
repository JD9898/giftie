import { Link } from 'expo-router';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🎁 Giftie</Text>
      <Text style={styles.tagline}>Your smart gift assistant</Text>

      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.button} onPress={() => { }}>
          <Text style={styles.buttonText}>➕ Add a Friend</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={() => { }}>
          <Text style={styles.buttonText}>🎁 Upcoming Gifts</Text>
        </TouchableOpacity>

        <Link href="/import-contacts" asChild>
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>📲 Import Contacts</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/friends-list" asChild>
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>👯‍♀️ Friends List</Text>
          </TouchableOpacity>
        </Link>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', paddingTop: 80, alignItems: 'center' },
  logo: { fontSize: 36, fontWeight: '800', marginBottom: 10, color: '#222' },
  tagline: { fontSize: 16, color: '#666', marginBottom: 40 },
  buttonContainer: { width: '80%' },
  button: {
    backgroundColor: '#222',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginBottom: 20,
  },
  buttonText: { color: '#fff', fontSize: 16, textAlign: 'center' },
});
