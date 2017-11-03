require "rails_helper"

RSpec.describe PostsClusterizer do
  describe ".clusterize" do
    subject { described_class.clusterize! }

    context "when there are only clusterized posts" do
      it "changes noting" do
        expect { subject }.not_to change { Post.non_clustered_posts.count }
      end
    end

    context "when there are non clusterized posts" do
      let(:non_clustered_posts_count) { 3 }
      let!(:non_clustered_posts) { create_list(:post, non_clustered_posts_count) }

      it "clusterizes theam all" do
        expect { subject }.to change { Post.non_clustered_posts.count }.from(non_clustered_posts_count).to(0)
      end
    end
  end
end
