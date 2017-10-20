require "rails_helper"

describe TopicsController, type: :request do
  describe "#show" do
    let(:do_request) { get "/topics/#{topic_id}" }

    context "when there is no topic for id" do
      let(:topic_id) { 404 }

      it "renders 404 page" do
        expect { do_request }.to raise_error(ActiveRecord::RecordNotFound)
      end
    end

    context "when there is a topic for id" do
      let(:topic) { create(:topic) }
      let(:topic_id) { topic.id }

      it "renders topic page" do
        do_request
        expect(response).to have_http_status(:ok)
      end
    end
  end
end
