import { useNavigation } from '@react-navigation/native';
import { Link } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { BACKEND_URL } from './import-contacts';

type RootStackParamList = {
  FriendHistory: { name: string };
  // add other routes if needed
};

export default function FriendsListScreen() {
  const navigation = useNavigation<import('@react-navigation/native').NavigationProp<RootStackParamList>>();
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchFriends = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/friends`);
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

  const saveGift = async (gift: GiftSuggestionResponse) => {
    await fetch(`${BACKEND_URL}/api/gift-history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(gift),
    });
  };

  const suggestGift = async (friend: Friend): Promise<void> => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/suggest-gift`, {
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

      Alert.alert(`Gift for ${data.recipient}`, `🎁 ${data.suggested_gift}`, [
        {
          text: 'Reject',
          style: 'cancel',
        },
        {
          text: 'Accept',
          onPress: () => saveGift(data),
        },
      ]);
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
            <Link href={`/friend-history/${item.name}`} asChild>
              <TouchableOpacity
                style={styles.friendItem}
                onPress={() => navigation.navigate('FriendHistory', { name: item.name })}
                activeOpacity={0.8}
              >
                <View style={{ flex: 1 }}>
                  <Text style={styles.friendName}>{item.name}</Text>
                  <Text style={styles.friendBirthday}>🎂 {item.birthday}</Text>
                </View>
                <TouchableOpacity

                  style={styles.button}
                  onPress={(e) => {
                    e.stopPropagation(); // Prevents triggering the outer touch
                    suggestGift(item);
                  }}
                >
                  <Text style={styles.buttonText}>Suggest Gift</Text>
                </TouchableOpacity>
              </TouchableOpacity>
            </Link>
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
