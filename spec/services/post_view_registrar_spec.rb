require "rails_helper"

RSpec.describe PostViewRegistrar do
  describe "#commit_view" do
    subject do
      described_class.new(post: post, user: user, user_ip: user_ip).commit_view
    end

    let(:post) { create(:post) }
    let(:user_ip) { "192.168.1.1" }

    context "when user is authorized" do
      let(:user) { create(:user) }

      context "and user hasn't seen the post" do
        it "creates a new post view for user and post" do
          expect { subject }.to change { PostView.count }
        end
      end

      context "and user has already seen the post" do
        let!(:post_view) { create(:post_view, user: user, post: post) }

        it "doesn't commit the view as a new view" do
          expect { subject }.not_to change { PostView.count }
        end
      end
    end

    context "when user is unauthorized" do
      let(:user) { nil }

      context "and there is no view for post from user ip" do
        it "creates a new post view for post and ip" do
          expect { subject }.to change { PostView.count }
        end
      end

      context "and there is a view for post from user ip" do
        let(:ip_hash) { "66efff4c945d3c3b87fc271b47d456db" }
        let!(:post_view) { create(:post_view, ip_hash: ip_hash, post: post) }

        it "doesn't commit the view as a new view" do
          expect { subject }.not_to change { PostView.count }
        end
      end
    end
  end
end
