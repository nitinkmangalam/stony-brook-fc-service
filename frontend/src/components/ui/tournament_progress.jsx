import { Trophy } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './card';

const TournamentProgressCard = ({ overviewData }) => {
  // Calculate whether to show total progress or phase progress
  const displayPercentage = overviewData.progress?.phasePercentage || 0;
  const displayTotal = overviewData.progress?.phaseTotalMatches || 25;
  const phase = overviewData.progress?.currentPhase || 'League Phase';

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Tournament Progress</CardTitle>
        <Trophy className="h-4 w-4 text-blue-600" />
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-2xl font-bold">{phase}</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${displayPercentage}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500">
            {overviewData.progress?.matchesPlayed || 0} of {displayTotal} matches played
            ({displayPercentage}% Complete)
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default TournamentProgressCard;