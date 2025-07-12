import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import {
    ActivityIndicator,
    FlatList,
    StyleSheet,
    Text,
    View,
} from 'react-native';
import { BACKEND_URL } from '../import-contacts'; // update path if needed

type GiftHistoryItem = {
    suggested_gift: string;
    sentiment: string;
};

export default function FriendHistoryScreen() {
    const { name } = useLocalSearchParams();
    const safeName = typeof name === 'string' ? name : '';

    const [history, setHistory] = useState<GiftHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const res = await fetch(
                    `${BACKEND_URL}/api/gift-history?recipient=${encodeURIComponent(
                        safeName
                    )}`
                );
                const data = await res.json();
                setHistory(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        if (safeName) {
            loadHistory();
        }
    }, [safeName]);

    if (!safeName) {
        return (
            <View style={styles.container}>
                <Text style={styles.empty}>Missing friend name.</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <Text style={styles.title}>🎁 Gift history for {safeName}</Text>
            {loading ? (
                <ActivityIndicator size="large" />
            ) : history.length === 0 ? (
                <Text style={styles.empty}>No gift history found.</Text>
            ) : (
                <FlatList
                    data={history}
                    keyExtractor={(item, index) => `${item.suggested_gift}-${index}`}
                    renderItem={({ item }) => (
                        <View style={styles.giftItem}>
                            <Text style={styles.gift}>🎁 {item.suggested_gift}</Text>
                            <Text style={styles.sentiment}>💬 {item.sentiment}</Text>
                        </View>
                    )}
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 20 },
    title: { fontSize: 22, fontWeight: 'bold', marginBottom: 10 },
    empty: { fontSize: 16, color: '#777' },
    giftItem: {
        paddingVertical: 10,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    gift: { fontSize: 16 },
    sentiment: { fontSize: 14, color: '#555' },
});
