require "rails_helper"

describe TopicsController, type: :request do
  describe "#show" do
    let(:topic) { create(:topic, posts: [post]) }
    let(:post) { create(:post) }

    context "without params" do
      let(:do_request) { get "/topics/#{topic.id}" }

      it "show a main page" do
        do_request

        expect(response).to have_http_status(:ok)
      end
    end
  end
end
