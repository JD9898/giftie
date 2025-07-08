import React, { useEffect, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    FlatList,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';

export default function FriendsListScreen() {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchFriends = async () => {
    try {
      const res = await fetch('https://64d8b695c546.ngrok-free.app/api/friends');
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setFriends(data);
    } catch (err) {
      console.error('Fetch error:', err);
      Alert.alert('Error', 'Could not load friends.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFriends();
  }, []);

interface Friend {
    name: string;
    birthday: string;
}

interface GiftSuggestionResponse {
    recipient: string;
    suggested_gift: string;
}

const suggestGift = async (friend: Friend): Promise<void> => {
    try {
        const res = await fetch('https://64d8b695c546.ngrok-free.app/api/suggest-gift', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: friend.name,
                birthday: friend.birthday,
                sentiment: 'close friend', // 🔧 Temporary placeholder
            }),
        });

        if (!res.ok) throw new Error(`Status ${res.status}`);
        const data: GiftSuggestionResponse = await res.json();

        Alert.alert(`Gift for ${data.recipient}`, `🎁 ${data.suggested_gift}`);
    } catch (err) {
        console.error('Suggest error:', err);
        Alert.alert('Error', 'Could not suggest a gift.');
    }
};

  return (
    <View style={styles.container}>
      <Text style={styles.title}>👯 Friends</Text>
      {loading ? (
        <ActivityIndicator size="large" />
      ) : friends.length === 0 ? (
        <Text style={styles.empty}>No friends found.</Text>
      ) : (
        <FlatList
          data={friends}
          keyExtractor={(item, index) => `${item.name}-${index}`}
          renderItem={({ item }) => (
            <View style={styles.friendItem}>
              <View style={{ flex: 1 }}>
                <Text style={styles.friendName}>{item.name}</Text>
                <Text style={styles.friendBirthday}>🎂 {item.birthday}</Text>
              </View>
              <TouchableOpacity style={styles.button} onPress={() => suggestGift(item)}>
                <Text style={styles.buttonText}>Suggest Gift</Text>
              </TouchableOpacity>
            </View>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  empty: { fontSize: 16, color: '#888' },
  friendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderColor: '#eee',
    paddingVertical: 10,
    gap: 12,
  },
  friendName: { fontSize: 18 },
  friendBirthday: { fontSize: 14, color: '#666' },
  button: {
    backgroundColor: '#007aff',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  buttonText: { color: '#fff', fontWeight: 'bold' },
});
