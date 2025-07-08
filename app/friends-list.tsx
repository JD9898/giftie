import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, FlatList, StyleSheet, Text, View } from 'react-native';

export default function FriendsListScreen() {
  const [friends, setFriends] = useState([]);
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
              <Text style={styles.friendName}>{item.name}</Text>
              <Text style={styles.friendBirthday}>🎂 {item.birthday}</Text>
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
    borderBottomWidth: 1,
    borderColor: '#eee',
    paddingVertical: 10,
  },
  friendName: { fontSize: 18 },
  friendBirthday: { fontSize: 14, color: '#666' },
});
